import os
import time
import sqlite3
import logging

from dataclasses import dataclass
from typing import Optional, Iterable, List, Dict

import requests
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


# --------------------------------------------------------------------------
# Config
# --------------------------------------------------------------------------

TWITTERAPI_IO_BASE_URL = "https://api.twitterapi.io"

TWITTERAPI_IO_KEY = os.environ.get(
    "TWITTERAPI_IO_KEY",
    ""
)


# How long a successful profile lookup stays valid.
PROFILE_TTL_SECONDS_OK = 24 * 60 * 60


# How long a failed lookup stays cached before retry.
PROFILE_TTL_SECONDS_ERROR = 60 * 60


# Minimum spacing between outbound profile requests.
MIN_SECONDS_BETWEEN_REQUESTS = 1.1


_last_request_time = 0.0


# --------------------------------------------------------------------------
# Profile result
# --------------------------------------------------------------------------

@dataclass
class ProfileResult:

    username: str

    status: str
    # "ok" | "error" | "not_found"

    account_created_at: Optional[str] = None

    followers: Optional[int] = None

    following: Optional[int] = None

    statuses_count: Optional[int] = None

    is_verified: Optional[bool] = None

    is_blue_verified: Optional[bool] = None

    fetched_at: Optional[float] = None

    from_cache: bool = False

    @property
    def is_known(self) -> bool:
        """
        True only when real profile data was successfully obtained.
        """

        return self.status == "ok"


# --------------------------------------------------------------------------
# Persistent cache
# --------------------------------------------------------------------------

def ensure_schema(conn: sqlite3.Connection) -> None:
    """
    Create the profile_cache table if it does not already exist.
    """

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS profile_cache (
            username TEXT PRIMARY KEY,
            fetched_at REAL NOT NULL,
            status TEXT NOT NULL,
            account_created_at TEXT,
            followers INTEGER,
            following INTEGER,
            statuses_count INTEGER,
            is_verified INTEGER,
            is_blue_verified INTEGER
        )
        """
    )

    conn.commit()


# --------------------------------------------------------------------------
# Convert DB row → ProfileResult
# --------------------------------------------------------------------------

def _row_to_result(
    row: sqlite3.Row
) -> ProfileResult:

    return ProfileResult(

        username=row["username"],

        status=row["status"],

        account_created_at=row[
            "account_created_at"
        ],

        followers=row[
            "followers"
        ],

        following=row[
            "following"
        ],

        statuses_count=row[
            "statuses_count"
        ],

        is_verified=(
            None
            if row["is_verified"] is None
            else bool(row["is_verified"])
        ),

        is_blue_verified=(
            None
            if row["is_blue_verified"] is None
            else bool(row["is_blue_verified"])
        ),

        fetched_at=row[
            "fetched_at"
        ],

        from_cache=True,
    )


# --------------------------------------------------------------------------
# Read cached profile
# --------------------------------------------------------------------------

def _get_cached(
    conn: sqlite3.Connection,
    username: str
) -> Optional[ProfileResult]:

    conn.row_factory = sqlite3.Row

    row = conn.execute(
        """
        SELECT *
        FROM profile_cache
        WHERE username = ?
        """,
        (
            username.lower(),
        )
    ).fetchone()

    if row is None:
        return None

    # Successful profile → 24 hour cache
    #
    # Failed profile → 1 hour cache
    ttl = (
        PROFILE_TTL_SECONDS_OK
        if row["status"] == "ok"
        else PROFILE_TTL_SECONDS_ERROR
    )

    age = (
        time.time()
        - row["fetched_at"]
    )

    if age > ttl:
        return None

    return _row_to_result(row)


# --------------------------------------------------------------------------
# Store profile in cache
# --------------------------------------------------------------------------

def _store(
    conn: sqlite3.Connection,
    result: ProfileResult
) -> None:

    conn.execute(
        """
        INSERT INTO profile_cache (
            username,
            fetched_at,
            status,
            account_created_at,
            followers,
            following,
            statuses_count,
            is_verified,
            is_blue_verified
        )

        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)

        ON CONFLICT(username)
        DO UPDATE SET
            fetched_at = excluded.fetched_at,
            status = excluded.status,
            account_created_at = excluded.account_created_at,
            followers = excluded.followers,
            following = excluded.following,
            statuses_count = excluded.statuses_count,
            is_verified = excluded.is_verified,
            is_blue_verified = excluded.is_blue_verified
        """,

        (
            result.username.lower(),

            result.fetched_at
            or time.time(),

            result.status,

            result.account_created_at,

            result.followers,

            result.following,

            result.statuses_count,

            (
                None
                if result.is_verified is None
                else int(result.is_verified)
            ),

            (
                None
                if result.is_blue_verified is None
                else int(result.is_blue_verified)
            ),
        )
    )

    conn.commit()


# --------------------------------------------------------------------------
# Network throttling
# --------------------------------------------------------------------------

def _throttle() -> None:
    """
    Enforce minimum spacing between actual HTTP requests.

    Cached requests do not trigger this.
    """

    global _last_request_time

    elapsed = (
        time.time()
        - _last_request_time
    )

    wait = (
        MIN_SECONDS_BETWEEN_REQUESTS
        - elapsed
    )

    if wait > 0:
        time.sleep(wait)

    _last_request_time = time.time()


# --------------------------------------------------------------------------
# TwitterAPI.io profile request
# --------------------------------------------------------------------------

def _fetch_from_api(username: str) -> ProfileResult:
    """
    Fetch a user profile from TwitterAPI.io.
    """

    if not TWITTERAPI_IO_KEY:
        logger.warning(
            "TWITTERAPI_IO_KEY is not set; cannot fetch profile for %s",
            username
        )

        return ProfileResult(
            username=username,
            status="error",
            fetched_at=time.time()
        )

    url = (
        f"{TWITTERAPI_IO_BASE_URL}"
        "/twitter/user/info"
    )

    headers = {
        "X-API-Key": TWITTERAPI_IO_KEY
    }

    params = {
        "userName": username
    }

    try:

        _throttle()

        response = requests.get(
            url,
            headers=headers,
            params=params,
            timeout=15
        )

        # ------------------------------------------------------
        # User not found
        # ------------------------------------------------------

        if response.status_code == 404:

            return ProfileResult(
                username=username,
                status="not_found",
                fetched_at=time.time()
            )

        # ------------------------------------------------------
        # API error
        # ------------------------------------------------------

        if not response.ok:

            logger.warning(
                "Profile fetch failed for %s: HTTP %d - %s",
                username,
                response.status_code,
                response.text[:300]
            )

            return ProfileResult(
                username=username,
                status="error",
                fetched_at=time.time()
            )

        # ------------------------------------------------------
        # Parse response
        # ------------------------------------------------------

        payload = response.json()

        # TwitterAPI.io response:
        #
        # {
        #     "status": "success",
        #     "msg": "success",
        #     "data": {
        #         ...
        #     }
        # }

        data = payload.get("data")

        if not isinstance(data, dict):

            logger.warning(
                "Invalid profile data returned for %s",
                username
            )

            return ProfileResult(
                username=username,
                status="error",
                fetched_at=time.time()
            )

        # ------------------------------------------------------
        # Build ProfileResult
        # ------------------------------------------------------

        return ProfileResult(

            username=data.get(
                "userName",
                username
            ),

            status="ok",

            account_created_at=data.get(
                "createdAt"
            ),

            followers=data.get(
                "followers"
            ),

            following=data.get(
                "following"
            ),

            statuses_count=data.get(
                "statusesCount"
            ),

            is_verified=data.get(
                "isVerified",
                False
            ),

            is_blue_verified=data.get(
                "isBlueVerified",
                False
            ),

            fetched_at=time.time(),

            from_cache=False
        )

    except requests.RequestException as error:

        logger.warning(
            "Profile request failed for %s: %s",
            username,
            error
        )

        return ProfileResult(
            username=username,
            status="error",
            fetched_at=time.time()
        )

    except ValueError as error:

        logger.warning(
            "Invalid JSON profile response for %s: %s",
            username,
            error
        )

        return ProfileResult(
            username=username,
            status="error",
            fetched_at=time.time()
        )

# --------------------------------------------------------------------------
# Public API
# --------------------------------------------------------------------------

def get_user_profile(
    username: str,
    conn: sqlite3.Connection
) -> ProfileResult:
    """
    Get a single user profile.

    Uses the persistent SQLite cache before making
    a TwitterAPI.io request.
    """

    cached = _get_cached(
        conn,
        username
    )

    if cached is not None:
        return cached


    result = _fetch_from_api(
        username
    )


    _store(
        conn,
        result
    )


    return result


# --------------------------------------------------------------------------
# Batch profile lookup
# --------------------------------------------------------------------------

def get_profiles_for_authors(
    usernames: Iterable[str],
    conn: sqlite3.Connection
) -> Dict[str, ProfileResult]:
    """
    Resolve profiles for multiple tweet authors.

    - Deduplicates usernames.
    - Uses cached profiles whenever possible.
    - Only makes requests for missing/stale profiles.
    - Returns an entry for every username.
    """

    unique_usernames = sorted(
        {
            u.lower()
            for u in usernames
            if u
        }
    )


    results: Dict[
        str,
        ProfileResult
    ] = {}


    to_fetch: List[str] = []


    # --------------------------------------------------------------
    # First check cache
    # --------------------------------------------------------------

    for username in unique_usernames:

        cached = _get_cached(
            conn,
            username
        )

        if cached is not None:

            results[username] = cached

        else:

            to_fetch.append(
                username
            )


    logger.info(
        "Profile enrichment: "
        "%d unique authors, "
        "%d served from cache, "
        "%d to fetch",

        len(unique_usernames),

        len(unique_usernames)
        - len(to_fetch),

        len(to_fetch)
    )


    # --------------------------------------------------------------
    # Fetch missing/stale profiles
    # --------------------------------------------------------------

    for username in to_fetch:

        result = _fetch_from_api(
            username
        )

        _store(
            conn,
            result
        )

        results[username] = result


    return results
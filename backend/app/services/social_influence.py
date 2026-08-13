import math
from datetime import datetime, timezone


def calculate_credibility_multiplier(
    account_created_at: datetime,
    followers: int,
    following: int,
    total_tweets: int,
    *,
    is_verified: bool = False,
    min_account_age_days: float = 30.0,
    max_follow_ratio: float = 50.0,
) -> float:
    """
    Calculate a 0-1 multiplier that discounts influence for accounts
    showing common bot / fake-engagement signatures.

    This is a heuristic, not a bot classifier -- it won't catch
    sophisticated bots, and it can false-flag legitimate new or
    low-activity accounts. Treat it as a soft discount, not a hard filter.
    """
    now = datetime.now(timezone.utc)
    account_age_days = max((now - account_created_at).total_seconds() / 86400, 0.0)

    # New accounts ramp up linearly to full credibility (pump farms
    # frequently use freshly created accounts).
    age_factor = min(account_age_days / min_account_age_days, 1.0)

    # Mass-following far more accounts than follow back is a classic
    # bot pattern. Ratio computed safely for zero followers.
    follow_ratio = following / max(followers, 1)
    ratio_factor = 1.0 if follow_ratio <= max_follow_ratio else max_follow_ratio / follow_ratio

    # Near-zero tweet history (freshly spun-up bots) or implausibly high
    # posting rate relative to age (spam/repost bots) both get penalized.
    tweets_per_day = total_tweets / max(account_age_days, 1.0)
    activity_factor = 1.0
    if total_tweets < 5:
        activity_factor = 0.3
    elif tweets_per_day > 100:
        activity_factor = 0.5

    multiplier = age_factor * ratio_factor * activity_factor

    # Verified / blue-verified accounts get a small credibility boost,
    # capped so it can never push a flagged account back to full trust
    # on its own.
    if is_verified:
        multiplier = min(multiplier * 1.15, 1.0)

    return round(min(max(multiplier, 0.0), 1.0), 4)


def calculate_social_influence(
    followers: int,
    likes: int,
    retweets: int,
    *,
    account_created_at: datetime | None = None,
    following: int | None = None,
    total_tweets: int | None = None,
    is_verified: bool = False,
    reach_weight: float = 0.45,
    engagement_weight: float = 0.55,
    reach_log_base: float = 6.0,
    engagement_log_base: float = 5.0,
    min_engagement_gate: float = 0.25,
) -> float:
    """
    Calculate a 0-100 Social Influence score for a single post.

    Social Influence answers ONE question: how influential is this
    account/tweet? It is built entirely from reach, engagement, and
    account credibility. Sentiment is intentionally NOT a factor here --
    a confidently-classified tweet from a nobody account is still a
    nobody account. Use calculate_signal_strength() to combine Social
    Influence with sentiment confidence for ranking purposes.

    Components:
      1. Reach potential   - based on follower count, log-scaled so a
                              1M-follower account doesn't fully eclipse
                              a 3K-follower one.
      2. Engagement        - based on raw likes/retweets (log-scaled,
                              NOT a ratio to followers -- a ratio lets
                              small accounts hit the ceiling trivially
                              off one lucky tweet). Additionally
                              "reach-gated": an account with near-zero
                              reach only gets partial credit for a viral
                              engagement spike, ramping to full credit
                              as reach grows. This stops a single viral
                              event on an unknown account from
                              outranking an established account.
      3. Credibility        - multiplier from calculate_credibility_multiplier,
                              penalizing likely bot / fake-engagement
                              accounts and (slightly) rewarding verified
                              ones.

    Args:
        followers: Account follower count.
        likes: Like count on the post.
        retweets: Retweet + quote-tweet count on the post.
        account_created_at: Account creation timestamp, for credibility check.
        following: Account following count, for credibility check.
        total_tweets: Lifetime tweet count, for credibility check.
        is_verified: Whether the account is verified/blue-verified.
        reach_weight: Weight of the reach component in the final blend.
        engagement_weight: Weight of the (gated) engagement component.
        reach_log_base: Calibration constant for reach scaling -- e.g. 6
            means 10^6 (1M) followers maps to a reach_score of 100. Tune
            to your platform's actual follower distribution.
        engagement_log_base: Calibration constant for engagement scaling --
            e.g. 5 means 10^5 (100k) weighted engagement points maps to
            an engagement_score of 100. Tune against real viral-tweet data.
        min_engagement_gate: Minimum fraction of engagement_score credited
            to a zero-reach account (0.25 = 25%). Ramps linearly to 1.0
            (full credit) as reach_score approaches 100.

    Returns:
        Social Influence score from 0 to 100.
    """
    followers = max(followers, 0)
    likes = max(likes, 0)
    retweets = max(retweets, 0)

    # 1. Reach potential
    reach_score = min(math.log10(followers + 1) / reach_log_base * 100, 100)

    # 2. Engagement (log-scaled raw counts, not a ratio -- see docstring)
    engagement = likes + (2 * retweets)
    engagement_score = min(math.log10(engagement + 1) / engagement_log_base * 100, 100)

    # Reach-gate the engagement contribution so a near-zero-reach account
    # can't fully dominate off one viral spike.
    engagement_gate = min_engagement_gate + (1 - min_engagement_gate) * (reach_score / 100)
    gated_engagement_score = engagement_score * engagement_gate

    base_score = (
        reach_weight * reach_score
        + engagement_weight * gated_engagement_score
    )

    credibility_multiplier = 1.0
    if account_created_at is not None and following is not None and total_tweets is not None:
        credibility_multiplier = calculate_credibility_multiplier(
            account_created_at=account_created_at,
            followers=followers,
            following=following,
            total_tweets=total_tweets,
            is_verified=is_verified,
        )

    final_score = base_score * credibility_multiplier
    return round(min(max(final_score, 0.0), 100.0), 2)


def calculate_signal_strength(
    social_influence: float,
    sentiment_confidence: float,
) -> float:
    """
    Calculate a 0-100 Signal Strength score.

    Signal Strength answers a DIFFERENT question than Social Influence:
    how much should this specific post move the needle on aggregate
    sentiment? It combines how influential the account/tweet is with how
    confidently the sentiment model classified it.

        Signal Strength = Social Influence x Sentiment Confidence

    Keeping this separate from calculate_social_influence() means Social
    Influence stays a pure account/tweet-influence metric (useful for
    "who are the most influential accounts talking about this coin"),
    while Signal Strength is the metric to use when weighting or ranking
    posts for sentiment aggregation.

    Args:
        social_influence: Output of calculate_social_influence() (0-100).
        sentiment_confidence: Model's confidence in the sentiment label, 0-1.

    Returns:
        Signal Strength score from 0 to 100.
    """
    sentiment_confidence = min(max(sentiment_confidence, 0.0), 1.0)
    return round(min(max(social_influence * sentiment_confidence, 0.0), 100.0), 2)


if __name__ == "__main__":
    established = dict(
        account_created_at=datetime(2019, 3, 14, tzinfo=timezone.utc),
        following=890,
        total_tweets=14_200,
    )
    brand_new = dict(
        account_created_at=datetime(2026, 8, 10, tzinfo=timezone.utc),
        following=980,
        total_tweets=2,
    )

    # Case A: 400 followers, 0 engagement, established account
    case_a = calculate_social_influence(followers=400, likes=0, retweets=0, **established)
    print(f"Case A (400 followers, established): {case_a}/100")

    # Case B: 400 followers, 0 engagement, brand-new/suspicious account
    case_b = calculate_social_influence(followers=400, likes=0, retweets=0, **brand_new)
    print(f"Case B (400 followers, brand-new/suspicious): {case_b}/100")

    # Case C: 125,000 followers, real engagement, established account
    case_c = calculate_social_influence(
        followers=125_000, likes=4_200, retweets=850, **established
    )
    print(f"Case C (125k followers, established, high engagement): {case_c}/100")

    # Case D: 6 followers, 0 engagement -- sentiment confidence is NOT
    # passed to calculate_social_influence() at all anymore.
    case_d = calculate_social_influence(followers=6, likes=0, retweets=0)
    print(f"Case D (6 followers, no engagement): {case_d}/100")

    # Signal Strength is calculated separately, only when you actually
    # want to blend in sentiment confidence.
    print(f"Signal Strength, Case C @ 0.77 sentiment confidence: "
          f"{calculate_signal_strength(case_c, 0.77)}")
    print(f"Signal Strength, Case D @ 0.99 sentiment confidence: "
          f"{calculate_signal_strength(case_d, 0.99)}")
import time
import logging

from backend.app.services.market_reaction_updater import (
    update_pending_reactions,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

CHECK_INTERVAL = 300  # 5 minutes


def run_scheduler():
    logging.info(
        "Market reaction scheduler started."
    )

    while True:
        try:
            updated = update_pending_reactions()

            logging.info(
                "Market reaction update completed. "
                "Updated %d tweets.",
                updated
            )

        except Exception:
            logging.exception(
                "Market reaction update failed."
            )

        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    run_scheduler()
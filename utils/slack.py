
"""Slack tizimga uzatilgan xabarni yuborish"""
import requests
import traceback

from core.config import config


def send_slack_message(exc, exc_type, exc_message):
    if config.slack.slack_channel_url:
        # Qisqa traceback olish (faqat birinchi 5 satrni)
        tb_list = traceback.format_exception(type(exc), exc, exc.__traceback__)
        short_tb = "".join(tb_list[-10:-1])  # 5 ta satrni oling yoki siz xohlagan satr miqdori

        headers = {
            "Content-Type": "application/json"
        }

        payload = {
            "username": f"{config.app.app_name} - logging",
            "icon_emoji": ":white_frowning_face:",
            "text": "Xatolik yuz berdi",
            "attachments": [
                {
                    "fallback": "Xatolik haqida qo'shimcha ma'lumot.",
                    "color": "#ff0000",
                    "pretext": "Xatolik xabari:",
                    "title": "Xatolik turi",
                    "text": f"{exc_type}: {exc_message}",
                    "footer": "Server"
                }
            ],
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"""*Traceback:*```{short_tb}```"""
                    }
                },
                {
                    "type": "divider"
                }
            ]
        }

        requests.post(
            config.slack.slack_channel_url,
            json=payload,
            headers=headers
        )

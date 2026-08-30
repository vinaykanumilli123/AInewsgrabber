import os
import html
import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from dotenv import load_dotenv


load_dotenv()


# ============================================================
# HELPERS
# ============================================================

def escape_text(value):
    """
    Safely convert text for HTML email.
    """
    return html.escape(
        value or ""
    )


def parse_stories(digest):
    """
    Convert the structured LLM output into
    individual news stories.
    """

    stories = []

    blocks = digest.split(
        "STORY_START"
    )

    for block in blocks:

        if "STORY_END" not in block:
            continue

        block = block.split(
            "STORY_END",
            1
        )[0]

        fields = {}

        current_key = None

        for line in block.splitlines():

            line = line.strip()

            if not line:
                continue

            if ":" in line:

                key, value = line.split(
                    ":",
                    1
                )

                key = key.strip()

                if key in [
                    "TITLE",
                    "WHAT_HAPPENED",
                    "WHY_IT_MATTERS",
                    "IN_SIMPLE_WORDS",
                    "CATEGORY",
                    "SOURCE",
                    "URL",
                ]:

                    current_key = key

                    fields[key] = (
                        value.strip()
                    )

                    continue

            # Handle multi-line values
            if current_key:
                fields[current_key] += (
                    " " + line
                )

        if fields.get("TITLE"):
            stories.append(fields)

    return stories


# ============================================================
# BUILD HTML EMAIL
# ============================================================

def build_html(stories):
    """
    Build a clean, professional HTML newsletter.

    The email is intentionally simple:
    - Strong editorial hierarchy
    - No unnecessary marketing language
    - Easy scanning
    - Clear explanations
    - Source link for every story
    """

    from datetime import datetime

    today = datetime.now().strftime(
        "%A · %B %d, %Y"
    )

    if not stories:
        story_html = """
        <div style="
            background: #ffffff;
            border: 1px solid #e2e5e9;
            border-radius: 10px;
            padding: 28px;
            color: #4b5563;
            font-size: 15px;
            line-height: 1.7;
        ">
            No significant AI stories were available today.
        </div>
        """
    else:
        story_html = ""

        for index, story in enumerate(
            stories,
            start=1
        ):
            title = escape_text(
                story.get(
                    "TITLE",
                    "Untitled story"
                )
            )

            happened = escape_text(
                story.get(
                    "WHAT_HAPPENED",
                    ""
                )
            )

            why = escape_text(
                story.get(
                    "WHY_IT_MATTERS",
                    ""
                )
            )

            simple = escape_text(
                story.get(
                    "IN_SIMPLE_WORDS",
                    ""
                )
            )

            category = escape_text(
                story.get(
                    "CATEGORY",
                    "AI News"
                )
            )

            source = escape_text(
                story.get(
                    "SOURCE",
                    ""
                )
            )

            url = escape_text(
                story.get(
                    "URL",
                    "#"
                )
            )

            story_html += f"""
            <div style="
                background: #ffffff;
                border: 1px solid #e2e5e9;
                border-radius: 10px;
                padding: 28px;
                margin-bottom: 18px;
            ">

                <!-- STORY META -->

                <div style="
                    margin-bottom: 11px;
                    font-size: 11px;
                    font-weight: 700;
                    letter-spacing: 1.1px;
                    text-transform: uppercase;
                    color: #6b7280;
                ">
                    {index:02d} · {category}
                </div>


                <!-- STORY TITLE -->

                <h2 style="
                    margin: 0 0 22px 0;
                    font-size: 22px;
                    line-height: 1.35;
                    font-weight: 700;
                    color: #111827;
                ">
                    {title}
                </h2>


                <!-- WHAT HAPPENED -->

                <div style="
                    margin-bottom: 20px;
                ">

                    <div style="
                        margin-bottom: 7px;
                        font-size: 12px;
                        font-weight: 700;
                        letter-spacing: 0.8px;
                        text-transform: uppercase;
                        color: #111827;
                    ">
                        What happened
                    </div>

                    <div style="
                        font-size: 15px;
                        line-height: 1.75;
                        color: #374151;
                    ">
                        {happened}
                    </div>

                </div>


                <!-- WHY IT MATTERS -->

                <div style="
                    margin-bottom: 20px;
                ">

                    <div style="
                        margin-bottom: 7px;
                        font-size: 12px;
                        font-weight: 700;
                        letter-spacing: 0.8px;
                        text-transform: uppercase;
                        color: #111827;
                    ">
                        Why it matters
                    </div>

                    <div style="
                        font-size: 15px;
                        line-height: 1.75;
                        color: #374151;
                    ">
                        {why}
                    </div>

                </div>


                <!-- TAKEAWAY -->

                <div style="
                    background: #f7f8fa;
                    border-left: 3px solid #111827;
                    padding: 15px 17px;
                    margin-bottom: 22px;
                ">

                    <div style="
                        margin-bottom: 6px;
                        font-size: 12px;
                        font-weight: 700;
                        letter-spacing: 0.8px;
                        text-transform: uppercase;
                        color: #111827;
                    ">
                        Takeaway
                    </div>

                    <div style="
                        font-size: 15px;
                        line-height: 1.7;
                        color: #374151;
                    ">
                        {simple}
                    </div>

                </div>


                <!-- SOURCE -->

                <div style="
                    font-size: 12px;
                    color: #6b7280;
                ">
                    {source}
                    &nbsp;·&nbsp;

                    <a
                        href="{url}"
                        style="
                            color: #111827;
                            font-weight: 600;
                            text-decoration: none;
                        "
                    >
                        Read source →
                    </a>
                </div>

            </div>
            """


    # ========================================================
    # COMPLETE EMAIL
    # ========================================================

    html_content = f"""
    <!DOCTYPE html>

    <html>

    <body style="
        margin: 0;
        padding: 0;
        background: #f5f6f7;
        font-family: Arial, Helvetica, sans-serif;
        color: #111827;
    ">

        <div style="
            width: 100%;
            max-width: 720px;
            margin: 0 auto;
            padding: 32px 16px;
        ">


            <!-- HEADER -->

            <div style="
                padding: 8px 4px 24px 4px;
                border-bottom: 2px solid #111827;
                margin-bottom: 22px;
            ">

                <div style="
                    font-size: 30px;
                    line-height: 1.1;
                    font-weight: 800;
                    letter-spacing: -0.8px;
                    color: #111827;
                ">
                    AI NEWS
                </div>

                <div style="
                    margin-top: 8px;
                    font-size: 13px;
                    line-height: 1.5;
                    color: #6b7280;
                ">
                    {today}
                </div>

            </div>


            <!-- NEWS -->

            {story_html}


            <!-- FOOTER -->

            <div style="
                border-top: 1px solid #dfe2e6;
                margin-top: 28px;
                padding-top: 18px;
                text-align: center;
                font-size: 11px;
                line-height: 1.6;
                color: #9ca3af;
            ">
                Daily AI news · Automatically generated
            </div>

        </div>

    </body>

    </html>
    """

    return html_content


# ============================================================
# SEND EMAIL
# ============================================================

def send_email(state):

    print("Sending email...")

    digest = state.get(
        "final_digest",
        ""
    )

    sender = os.getenv(
        "SMTP_USERNAME"
    )

    password = os.getenv(
        "SMTP_PASSWORD"
    )

    recipient = os.getenv(
        "EMAIL_TO"
    )


    # ========================================================
    # VALIDATE CONFIGURATION
    # ========================================================

    if not sender:

        raise ValueError(
            "SMTP_USERNAME is not configured."
        )

    if not password:

        raise ValueError(
            "SMTP_PASSWORD is not configured."
        )

    if not recipient:

        raise ValueError(
            "EMAIL_TO is not configured."
        )


    # ========================================================
    # PARSE DIGEST
    # ========================================================

    stories = parse_stories(
        digest
    )

    print(
        f"Email contains "
        f"{len(stories)} stories."
    )


    # ========================================================
    # BUILD HTML
    # ========================================================

    html_content = build_html(
        stories
    )


    # ========================================================
    # CREATE EMAIL
    # ========================================================

    message = MIMEMultipart(
        "alternative"
    )

    message["Subject"] = "AI News · Daily Briefing"

    message["From"] = sender
    message["To"] = recipient


    # ========================================================
    # PLAIN TEXT FALLBACK
    # ========================================================

    message.attach(
        MIMEText(
            digest,
            "plain",
            "utf-8"
        )
    )


    # ========================================================
    # HTML VERSION
    # ========================================================

    message.attach(
        MIMEText(
            html_content,
            "html",
            "utf-8"
        )
    )


    # ========================================================
    # SMTP CONFIGURATION
    # ========================================================

    smtp_host = os.getenv(
        "SMTP_HOST",
        "smtp.gmail.com"
    )

    smtp_port = int(
        os.getenv(
            "SMTP_PORT",
            "587"
        )
    )


    # ========================================================
    # SEND EMAIL
    # ========================================================

    try:

        with smtplib.SMTP(
            smtp_host,
            smtp_port
        ) as server:

            server.starttls()

            server.login(
                sender,
                password
            )

            server.sendmail(
                sender,
                recipient,
                message.as_string()
            )

        print(
            "Email sent successfully!"
        )

    except smtplib.SMTPAuthenticationError:

        print(
            "Gmail authentication failed."
        )

        print(
            "Check your Gmail address "
            "and 16-character App Password."
        )

        raise

    except Exception as e:

        print(
            f"Email failed: {e}"
        )

        raise


    return {}

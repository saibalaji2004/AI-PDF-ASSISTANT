
from reportlab.platypus import (

    SimpleDocTemplate,

    Paragraph,

    Spacer
)

from reportlab.lib.styles import (

    getSampleStyleSheet
)

import os


def export_chat_pdf(

    session_title,

    pdf_name,

    messages,

    output_path
):

    doc = SimpleDocTemplate(

        output_path
    )

    styles = getSampleStyleSheet()

    elements = []

    elements.append(

        Paragraph(

            f"Chat Session: {session_title}",

            styles["Title"]
        )
    )

    elements.append(

        Paragraph(

            f"PDF: {pdf_name}",

            styles["Normal"]
        )
    )

    elements.append(

        Spacer(1, 20)
    )

    for msg in messages:

        role = msg.role.upper()

        text = msg.message

        elements.append(

            Paragraph(

                f"<b>{role}</b>: {text}",

                styles["BodyText"]
            )
        )

        elements.append(

            Spacer(1, 10)
        )

    doc.build(elements)

    return output_path

from flask import Flask, render_template, request, send_file
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
import io
from datetime import datetime
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30,leftMargin=30, topMargin=30,bottomMargin=18)
    elements = []
    styles = getSampleStyleSheet()

    factuurnummer = datetime.now().strftime("%Y%m%d-%H%M%S")
    datum = datetime.now().strftime("%d-%m-%Y")

    # Logo bovenaan
    logo_path = os.path.join('static', 'logo.png')
    if os.path.exists(logo_path):
        elements.append(Image(logo_path, width=120, height=50))
        elements.append(Spacer(1, 20))

    elements.append(Paragraph(f"Factuur #{factuurnummer}", styles['Title']))
    elements.append(Paragraph(f"Datum: {datum}", styles['Normal']))
    elements.append(Spacer(1, 20))

    klant_counter = int(request.form.get("klantCounter", 0))
    totaal_factuur = 0.0

    for k in range(1, klant_counter+1):
        naam = request.form.get(f"klantnaam_{k}")
        mobiel = request.form.get(f"mobiel_{k}")

        elements.append(Paragraph(f"Klant {k}: {naam} | Mobiel: {mobiel}", styles['Heading3']))
        elements.append(Spacer(1,5))

        data = [["Productnaam","Aantal","Inkoopprijs (SRD)","Fee (%)","Verkoopprijs (SRD)"]]

        product_list = request.form.getlist(f"product_{k}[]")
        aantal_list = request.form.getlist(f"aantal_{k}[]")
        inkoop_list = request.form.getlist(f"inkoop_{k}[]")
        fee_list = request.form.getlist(f"fee_{k}[]")

        totaal_verkoop = 0.0

        for i in range(len(product_list)):
            aantal = int(aantal_list[i])
            inkoop = float(inkoop_list[i])
            fee = float(fee_list[i])
            verkoop = aantal * inkoop * (1 + fee/100)
            totaal_verkoop += verkoop

            data.append([
                product_list[i],
                str(aantal),
                f"SRD{inkoop:.2f}",
                f"{fee:.2f}%",
                f"SRD{verkoop:.2f}"
            ])

        totaal_factuur += totaal_verkoop

        table = Table(data, colWidths=[150, 60, 80, 60, 80])
        style = TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#add8e6')),
            ('ALIGN',(0,0),(-1,-1),'CENTER'),
            ('GRID',(0,0),(-1,-1),1,colors.black),
            ('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),
            ('BACKGROUND', (0,1), (-1,-1), colors.whitesmoke)
        ])
        table.setStyle(style)
        elements.append(table)

        elements.append(Spacer(1,5))
        elements.append(Paragraph(f"Totaal verkoopprijs klant {naam}: SRD{totaal_verkoop:.2f}", styles['Normal']))
        elements.append(Spacer(1,20))

    # Totaal factuurbedrag groot en opvallend
    elements.append(Spacer(1,10))
    elements.append(Paragraph(f"Totaal factuurbedrag: SRD{totaal_factuur:.2f}", styles['Heading2']))

    doc.build(elements)
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name=f"factuur_{factuurnummer}.pdf", mimetype='application/pdf')

if __name__ == '__main__':
    app.run(debug=True)

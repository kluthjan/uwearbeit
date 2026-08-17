#!/usr/bin/env python3
"""
PDF-Generator für Gruppenarbeit 4
Gruppe 4: Jan, Marian, Mathias, Marco
Webserver mit SSH-Fernadministration
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfgen import canvas
from reportlab.platypus.flowables import Flowable
import os
import sys

# Color Palette
DARK_BLUE = colors.HexColor('#1a237e')
MED_BLUE = colors.HexColor('#1565C0')
LIGHT_BLUE = colors.HexColor('#42A5F5')
ACCENT_BLUE = colors.HexColor('#4fc3f7')
DARK_BG = colors.HexColor('#0d1b2a')
LIGHT_GRAY = colors.HexColor('#f5f5f5')
MED_GRAY = colors.HexColor('#e0e0e0')
DARK_GRAY = colors.HexColor('#424242')
TEXT_DARK = colors.HexColor('#212121')
TEXT_MEDIUM = colors.HexColor('#555555')
GREEN_OK = colors.HexColor('#2e7d32')
ORANGE_WARN = colors.HexColor('#e65100')
RED_ERR = colors.HexColor('#b71c1c')
CODE_BG = colors.HexColor('#1e1e2e')
CODE_FG = colors.HexColor('#cdd6f4')

OUT_DIR = "/home/jank/Schreibtisch/uweprojekt2/Gruppenarbeit4/docs"
os.makedirs(OUT_DIR, exist_ok=True)


def get_styles():
    """Define all paragraph styles."""
    styles = {}

    styles['h1'] = ParagraphStyle(
        'H1', fontName='Helvetica-Bold', fontSize=24,
        textColor=DARK_BLUE, spaceBefore=12, spaceAfter=8,
        alignment=TA_CENTER
    )
    styles['h2'] = ParagraphStyle(
        'H2', fontName='Helvetica-Bold', fontSize=16,
        textColor=MED_BLUE, spaceBefore=16, spaceAfter=6,
        borderPad=4
    )
    styles['h3'] = ParagraphStyle(
        'H3', fontName='Helvetica-Bold', fontSize=13,
        textColor=DARK_BLUE, spaceBefore=12, spaceAfter=4
    )
    styles['h4'] = ParagraphStyle(
        'H4', fontName='Helvetica-Bold', fontSize=11,
        textColor=MED_BLUE, spaceBefore=8, spaceAfter=3
    )
    styles['body'] = ParagraphStyle(
        'Body', fontName='Helvetica', fontSize=10,
        textColor=TEXT_DARK, spaceBefore=3, spaceAfter=3,
        leading=15, alignment=TA_JUSTIFY
    )
    styles['body_left'] = ParagraphStyle(
        'BodyLeft', fontName='Helvetica', fontSize=10,
        textColor=TEXT_DARK, spaceBefore=3, spaceAfter=3,
        leading=15, alignment=TA_LEFT
    )
    styles['bullet'] = ParagraphStyle(
        'Bullet', fontName='Helvetica', fontSize=10,
        textColor=TEXT_DARK, spaceBefore=2, spaceAfter=2,
        leftIndent=20, bulletIndent=10, leading=14
    )
    styles['code'] = ParagraphStyle(
        'Code', fontName='Courier', fontSize=9,
        textColor=CODE_FG, backColor=CODE_BG,
        spaceBefore=3, spaceAfter=3, leading=13,
        leftIndent=10, rightIndent=10,
        borderPad=8
    )
    styles['code_inline'] = ParagraphStyle(
        'CodeInline', fontName='Courier-Bold', fontSize=10,
        textColor=colors.HexColor('#89b4fa'),
        backColor=CODE_BG, spaceBefore=0, spaceAfter=0
    )
    styles['note'] = ParagraphStyle(
        'Note', fontName='Helvetica-Oblique', fontSize=9,
        textColor=colors.HexColor('#5c6bc0'),
        spaceBefore=4, spaceAfter=4, leftIndent=15
    )
    styles['warning'] = ParagraphStyle(
        'Warning', fontName='Helvetica-Bold', fontSize=10,
        textColor=ORANGE_WARN, spaceBefore=4, spaceAfter=4,
        leftIndent=15
    )
    styles['success'] = ParagraphStyle(
        'Success', fontName='Helvetica-Bold', fontSize=10,
        textColor=GREEN_OK, spaceBefore=4, spaceAfter=4,
        leftIndent=15
    )
    styles['center'] = ParagraphStyle(
        'Center', fontName='Helvetica', fontSize=10,
        textColor=TEXT_DARK, alignment=TA_CENTER,
        spaceBefore=4, spaceAfter=4
    )
    styles['title_page'] = ParagraphStyle(
        'TitlePage', fontName='Helvetica-Bold', fontSize=32,
        textColor=colors.white, alignment=TA_CENTER,
        spaceBefore=0, spaceAfter=10
    )
    styles['subtitle'] = ParagraphStyle(
        'Subtitle', fontName='Helvetica', fontSize=14,
        textColor=ACCENT_BLUE, alignment=TA_CENTER,
        spaceBefore=4, spaceAfter=4
    )
    styles['step_number'] = ParagraphStyle(
        'StepNumber', fontName='Helvetica-Bold', fontSize=18,
        textColor=colors.white, alignment=TA_CENTER
    )
    return styles


def make_code_block(text, styles):
    """Create a styled code block."""
    lines = text.strip().split('\n')
    elements = []
    for line in lines:
        # Escape special chars for reportlab
        safe = line.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        elements.append(Paragraph(safe, styles['code']))
    return elements


def make_info_table(data, col_widths=None):
    """Create a styled info table."""
    if col_widths is None:
        col_widths = [5*cm, 10*cm]

    table = Table(data, colWidths=col_widths)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), DARK_BLUE),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, LIGHT_GRAY]),
        ('GRID', (0, 0), (-1, -1), 0.5, MED_GRAY),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        ('TEXTCOLOR', (0, 1), (0, -1), MED_BLUE),
    ]))
    return table


def make_step_box(number, title, styles):
    """Create a numbered step header box."""
    data = [[
        Paragraph(str(number), styles['step_number']),
        Paragraph(f'<b>{title}</b>', ParagraphStyle(
            'StepTitle', fontName='Helvetica-Bold', fontSize=13,
            textColor=colors.white, alignment=TA_LEFT
        ))
    ]]
    t = Table(data, colWidths=[1.5*cm, 14*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), MED_BLUE),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (0, -1), 6),
        ('LEFTPADDING', (1, 0), (1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('ROUNDEDCORNERS', [6, 6, 6, 6]),
    ]))
    return t


def page_header_footer(canvas_obj, doc, title="", team="Gruppe 4 | Jan, Marian, Mathias, Marco"):
    """Draw header and footer on every page."""
    w, h = A4
    canvas_obj.saveState()

    # Header Bar
    canvas_obj.setFillColor(DARK_BLUE)
    canvas_obj.rect(0, h - 40, w, 40, fill=1, stroke=0)
    canvas_obj.setFillColor(colors.white)
    canvas_obj.setFont('Helvetica-Bold', 11)
    canvas_obj.drawString(1.5*cm, h - 25, "Müller & Partner GmbH")
    canvas_obj.setFont('Helvetica', 9)
    canvas_obj.drawRightString(w - 1.5*cm, h - 25, f"Gruppenarbeit 4 | {title}")

    # Footer
    canvas_obj.setFillColor(DARK_BLUE)
    canvas_obj.rect(0, 0, w, 28, fill=1, stroke=0)
    canvas_obj.setFillColor(colors.white)
    canvas_obj.setFont('Helvetica', 8)
    canvas_obj.drawString(1.5*cm, 10, team)
    canvas_obj.drawCentredString(w/2, 10, "Webserver mit SSH-Fernadministration | 172.16.40.0/24")
    canvas_obj.drawRightString(w - 1.5*cm, 10, f"Seite {doc.page}")

    # Accent Line
    canvas_obj.setFillColor(ACCENT_BLUE)
    canvas_obj.rect(0, 28, w, 3, fill=1, stroke=0)
    canvas_obj.rect(0, h - 40, w, 3, fill=1, stroke=0)

    canvas_obj.restoreState()


# =============================================================================
# DOKUMENT 1: TEAM-ANLEITUNG (Windows-Benutzer)
# =============================================================================
def create_team_guide():
    """Create the comprehensive team guide PDF."""
    path = os.path.join(OUT_DIR, "Team_Anleitung_Gruppenarbeit4.pdf")
    styles = get_styles()

    def header_footer(c, d):
        page_header_footer(c, d, "Team-Anleitung")

    doc = SimpleDocTemplate(
        path, pagesize=A4,
        leftMargin=1.8*cm, rightMargin=1.8*cm,
        topMargin=2.5*cm, bottomMargin=2*cm,
        onFirstPage=header_footer, onLaterPages=header_footer
    )

    story = []
    W = A4[0] - 3.6*cm  # usable width

    # ===================== TITELSEITE =====================
    # Title background box
    title_data = [[Paragraph(
        "Gruppenarbeit 4<br/><font size='20'>Webserver mit SSH-Fernadministration</font>",
        styles['title_page']
    )]]
    title_box = Table(title_data, colWidths=[W])
    title_box.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), DARK_BLUE),
        ('TOPPADDING', (0, 0), (-1, -1), 30),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 30),
        ('LEFTPADDING', (0, 0), (-1, -1), 20),
        ('RIGHTPADDING', (0, 0), (-1, -1), 20),
    ]))
    story.append(title_box)
    story.append(Spacer(1, 0.5*cm))

    # Team Info Box
    team_info = [
        ['👥 Team Gruppe 4', ''],
        ['Jan', 'Teamleiter'],
        ['Marian', 'Teammitglied'],
        ['Mathias', 'Teammitglied'],
        ['Marco', 'Teammitglied'],
    ]
    ti = Table(team_info, colWidths=[8*cm, 7*cm])
    ti.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), MED_BLUE),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('SPAN', (0, 0), (-1, 0)),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, LIGHT_GRAY]),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('GRID', (0, 0), (-1, -1), 0.5, MED_GRAY),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(ti)
    story.append(Spacer(1, 0.3*cm))

    # Network Info
    net_info = [
        ['🌐 Netzwerk', '172.16.40.0/24'],
        ['🖥️ Server IP', '172.16.40.10'],
        ['💻 Client IP', '172.16.40.100'],
        ['🔒 SSH Port', '22'],
        ['🌍 HTTP Port', '80'],
        ['🌐 Hostname', 'server.gruppe4.local'],
    ]
    ni = Table(net_info, colWidths=[8*cm, 7*cm])
    ni.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), DARK_BLUE),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 1), (1, -1), 'Courier-Bold'),
        ('TEXTCOLOR', (1, 1), (1, -1), MED_BLUE),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, LIGHT_GRAY]),
        ('GRID', (0, 0), (-1, -1), 0.5, MED_GRAY),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(ni)
    story.append(Spacer(1, 0.5*cm))

    note_box = Table([[Paragraph(
        "📋 Diese Anleitung erklärt Schritt für Schritt die Einrichtung von Server- und Client-VM. "
        "Alle Schritte gelten für Linux (Debian/Ubuntu). Die Anleitung ist für Windows-Nutzer geschrieben, "
        "die VirtualBox nutzen.",
        styles['body']
    )]], colWidths=[W])
    note_box.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#e3f2fd')),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('BOX', (0, 0), (-1, -1), 1, MED_BLUE),
    ]))
    story.append(note_box)
    story.append(PageBreak())

    # ===================== INHALTSVERZEICHNIS =====================
    story.append(Paragraph("Inhaltsverzeichnis", styles['h1']))
    story.append(Spacer(1, 0.3*cm))

    toc = [
        ['1.', 'Aufgabenstellung & Netzwerkplan', '3'],
        ['2.', 'VirtualBox vorbereiten (Windows)', '4'],
        ['3.', 'Linux Server-VM einrichten', '5'],
        ['4.', 'SSH-Server konfigurieren', '7'],
        ['5.', 'Apache Webserver installieren', '9'],
        ['6.', 'Firewall (UFW) einrichten', '11'],
        ['7.', 'Client-VM einrichten', '12'],
        ['8.', 'SSH-Verbindung vom Client', '13'],
        ['9.', 'Webseite über Browser öffnen', '14'],
        ['10.', 'Netzwerkanalyse mit Wireshark', '15'],
        ['11.', 'Funktionstests & Dokumentation', '16'],
        ['12.', 'Häufige Probleme & Lösungen', '17'],
    ]
    toc_table = Table(toc, colWidths=[1.2*cm, 12*cm, 2*cm])
    toc_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('TEXTCOLOR', (0, 0), (0, -1), MED_BLUE),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
        ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, LIGHT_GRAY]),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
    ]))
    story.append(toc_table)
    story.append(PageBreak())

    # ===================== KAPITEL 1: AUFGABENSTELLUNG =====================
    story.append(Paragraph("1. Aufgabenstellung & Netzwerkplan", styles['h2']))
    story.append(HRFlowable(width=W, thickness=2, color=MED_BLUE))
    story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph("Kundenauftrag (Gruppenarbeit 4)", styles['h3']))
    story.append(Paragraph(
        "Die fiktive <b>Müller &amp; Partner GmbH</b> möchte für ihre Mitarbeiter ein internes Intranet bereitstellen. "
        "Auf diesem sollen Informationen, Ankündigungen und interne Hinweise veröffentlicht werden. "
        "Da der Server nicht direkt am Arbeitsplatz steht, soll er über SSH fernverwaltet werden.",
        styles['body']
    ))
    story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph("Zu installierende Dienste:", styles['h4']))
    services = [
        ['Dienst', 'Zweck', 'Port'],
        ['Apache2 (HTTP)', 'Webserver für das Intranet', '80/TCP'],
        ['OpenSSH (SSH)', 'Sichere Fernadministration', '22/TCP'],
        ['UFW Firewall', 'Schutz des Servers', 'alle Ports'],
    ]
    story.append(make_info_table(services, [6*cm, 7*cm, 3*cm]))
    story.append(Spacer(1, 0.4*cm))

    story.append(Paragraph("Netzwerkplan – Gruppe 4", styles['h3']))
    net_plan = [
        ['Gerät/Dienst', 'IP-Adresse', 'Funktion'],
        ['Netzwerk', '172.16.40.0/24', 'Internes VM-Netzwerk'],
        ['Server (Host)', '172.16.40.10', 'SSH + Apache Webserver'],
        ['Client', '172.16.40.100', 'Browser + SSH-Client'],
        ['Subnetzmaske', '255.255.255.0 (/24)', '—'],
        ['Standard-Gateway', '172.16.40.1', 'Virtuell (VirtualBox)'],
    ]
    story.append(make_info_table(net_plan, [5*cm, 5.5*cm, 5*cm]))
    story.append(Spacer(1, 0.4*cm))

    story.append(Paragraph("DNS-Einträge:", styles['h4']))
    dns = [
        ['Hostname', 'Typ', 'IP-Adresse'],
        ['server.gruppe4.local', 'A', '172.16.40.10'],
        ['intranet.gruppe4.local', 'A', '172.16.40.10'],
    ]
    story.append(make_info_table(dns, [7*cm, 3*cm, 5.5*cm]))
    story.append(PageBreak())

    # ===================== KAPITEL 2: VIRTUALBOX =====================
    story.append(Paragraph("2. VirtualBox vorbereiten (Windows-Nutzer)", styles['h2']))
    story.append(HRFlowable(width=W, thickness=2, color=MED_BLUE))
    story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph("VirtualBox herunterladen und installieren:", styles['h3']))
    vbox_steps = [
        "Öffne deinen Browser und gehe zu: https://www.virtualbox.org/wiki/Downloads",
        "Klicke auf 'Windows hosts' → Lade die .exe herunter",
        "Führe den Installer aus (als Administrator) und klicke durch 'Next'",
        "Nach Installation starte VirtualBox",
    ]
    for i, s in enumerate(vbox_steps, 1):
        story.append(Paragraph(f"<b>{i}.</b> {s}", styles['bullet']))
    story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph("Netzwerk in VirtualBox konfigurieren (Internes Netz):", styles['h3']))
    story.append(Paragraph(
        "Damit Server-VM und Client-VM miteinander kommunizieren können, müssen beide VMs "
        "im selben <b>Internen Netzwerk</b> sein:",
        styles['body']
    ))
    net_steps = [
        "VM auswählen → Klick auf 'Ändern' (Settings)",
        "Klick auf 'Netzwerk' (links)",
        "Adapter 1: Aktiviert ✓",
        "Angeschlossen an: 'Internes Netzwerk' wählen",
        "Name: intnet-gruppe4 eingeben",
        "OK klicken",
        "Das Gleiche für BEIDE VMs (Server UND Client)!",
    ]
    for i, s in enumerate(net_steps, 1):
        story.append(Paragraph(f"<b>{i}.</b> {s}", styles['bullet']))

    story.append(Spacer(1, 0.3*cm))
    warn_box = Table([[Paragraph(
        "⚠️ WICHTIG: Beide VMs müssen den exakt gleichen Netzwerknamen 'intnet-gruppe4' haben, "
        "sonst können sie nicht miteinander kommunizieren!",
        styles['warning']
    )]], colWidths=[W])
    warn_box.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#fff8e1')),
        ('BOX', (0, 0), (-1, -1), 1.5, ORANGE_WARN),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(warn_box)
    story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph("Linux ISO herunterladen:", styles['h3']))
    story.append(Paragraph(
        "Wir empfehlen <b>Ubuntu Server 22.04 LTS</b> für den Server und "
        "<b>Ubuntu Desktop 22.04 LTS</b> für den Client:",
        styles['body']
    ))
    iso_links = [
        ['Ubuntu Server 22.04', 'https://ubuntu.com/download/server', 'Für SERVER-VM'],
        ['Ubuntu Desktop 22.04', 'https://ubuntu.com/download/desktop', 'Für CLIENT-VM'],
    ]
    story.append(make_info_table(iso_links, [5*cm, 8*cm, 3.5*cm]))
    story.append(Spacer(1, 0.4*cm))

    story.append(Paragraph("Netzwerk-Modi & Portweiterleitung (Wichtig für Windows-Nutzer):", styles['h3']))
    story.append(Paragraph(
        "Es gibt zwei Szenarien, wie auf die Server-VM zugegriffen werden kann:",
        styles['body']
    ))

    port_info = [
        ['Szenario', 'VirtualBox Netzwerk-Typ', 'Portweiterleitung nötig?', 'Zugriff über'],
        ['1. Client-VM → Server-VM', 'Internes Netzwerk (intnet-gruppe4)', 'NEIN (alle Ports frei)', 'http://172.16.40.10\nssh admin@172.16.40.10'],
        ['2. Windows-Host → Server-VM', 'NAT mit Portweiterleitung', 'JA (Port 2222 & 8080)', 'http://localhost:8080\nssh admin@localhost -p 2222'],
        ['3. Windows-Host → Server-VM', 'Host-Only Adapter (Adapter 2)', 'NEIN (eigenes Netz)', 'http://172.16.40.10'],
    ]
    story.append(make_info_table(port_info, [4.2*cm, 4.5*cm, 3.5*cm, 4.3*cm]))
    story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph("Anleitung: Portweiterleitung in VirtualBox einrichten (für Windows-PC):", styles['h4']))
    pf_steps = [
        "Server-VM in VirtualBox auswählen → Einstellungen → Netzwerk",
        "Adapter 1: NAT auswählen (für Internet & Host-Zugriff)",
        "Klick auf 'Erweitert' → Klick auf den Button 'Portweiterleitung'",
        "Regel 1 hinzufügen: Name: SSH | Protokoll: TCP | Host-Port: 2222 | Gast-Port: 22",
        "Regel 2 hinzufügen: Name: HTTP | Protokoll: TCP | Host-Port: 8080 | Gast-Port: 80",
        "Auf dem Windows-PC im Browser öffnen: http://localhost:8080",
        "Auf dem Windows-PC in PuTTY / CMD ausführen: ssh admin@localhost -p 2222",
    ]
    for i, s in enumerate(pf_steps, 1):
        story.append(Paragraph(f"<b>{i}.</b> {s}", styles['bullet']))

    story.append(PageBreak())

    # ===================== KAPITEL 3: SERVER-VM =====================
    story.append(Paragraph("3. Linux Server-VM einrichten", styles['h2']))
    story.append(HRFlowable(width=W, thickness=2, color=MED_BLUE))
    story.append(Spacer(1, 0.2*cm))

    story.append(Paragraph("Neue VM in VirtualBox erstellen:", styles['h3']))
    vm_steps = [
        "VirtualBox öffnen → 'Neu' klicken",
        "Name: server-gruppe4 | Typ: Linux | Version: Ubuntu (64-bit)",
        "RAM: mindestens 2048 MB (2 GB) empfohlen",
        "Festplatte: Neue virtuelle Festplatte erstellen (20 GB)",
        "ISO einlegen: Einstellungen → Massenspeicher → CD-Symbol → Ubuntu Server ISO auswählen",
        "VM starten und Ubuntu installieren",
    ]
    for i, s in enumerate(vm_steps, 1):
        story.append(Paragraph(f"<b>{i}.</b> {s}", styles['bullet']))
    story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph("Ubuntu Server Installation:", styles['h3']))
    ubuntu_install = [
        "Sprache: English (empfohlen für Server)",
        "Tastaturlayout: German",
        "Netzwerk: Erstmal überspringen (konfigurieren wir manuell)",
        "Benutzername: admin | Computername: server-gruppe4",
        "Passwort: Admin1234! (oder eigenes sicheres Passwort)",
        "SSH installieren: ✓ OpenSSH server installieren (Haken setzen!)",
        "Installation abwarten → Neustarten",
    ]
    for i, s in enumerate(ubuntu_install, 1):
        story.append(Paragraph(f"<b>{i}.</b> {s}", styles['bullet']))
    story.append(Spacer(1, 0.3*cm))

    story.append(make_step_box("🚀", "SCHNELLE METHODE: Automatisches Setup-Skript (Empfohlen!)", styles))
    story.append(Spacer(1, 0.15*cm))
    story.append(Paragraph(
        "Statt alle Befehle manuell abzutippen, kannst du das vorgefertigte Automatisierungsskript "
        "direkt in der Server-VM ausführen (benötigt kurz Internet oder lokales Skript):",
        styles['body']
    ))
    for line in make_code_block(
        "# Server-VM vollautomatisch einrichten (IP 172.16.40.10, SSH, Apache, UFW):\n"
        "curl -sSL https://raw.githubusercontent.com/kluthjan/uwearbeit/main/scripts/server_setup.sh | sudo bash",
        styles):
        story.append(line)
    story.append(Spacer(1, 0.3*cm))

    # STEP BOX
    story.append(make_step_box("A", "MANUELLE METHODE: Netzwerk konfigurieren", styles))
    story.append(Spacer(1, 0.15*cm))

    story.append(Paragraph("Netzwerk-Interface herausfinden:", styles['h4']))
    for line in make_code_block("ip addr show\n# oder:\nip link show", styles):
        story.append(line)
    story.append(Spacer(1, 0.2*cm))

    story.append(Paragraph(
        "Den Interface-Namen merken (z.B. <b>enp0s3</b> oder <b>eth0</b>). "
        "Dann Netplan-Konfiguration editieren:",
        styles['body']
    ))

    for line in make_code_block(
        "sudo nano /etc/netplan/00-installer-config.yaml", styles):
        story.append(line)
    story.append(Spacer(1, 0.2*cm))

    story.append(Paragraph("Inhalt ersetzen mit (Interface-Name anpassen!):", styles['h4']))
    for line in make_code_block(
        "network:\n  version: 2\n  renderer: networkd\n  ethernets:\n"
        "    enp0s3:          # <-- Deinen Interface-Namen eintragen!\n"
        "      addresses:\n        - 172.16.40.10/24\n"
        "      routes:\n        - to: default\n          via: 172.16.40.1\n"
        "      nameservers:\n        addresses: [8.8.8.8]\n      dhcp4: false",
        styles):
        story.append(line)
    story.append(Spacer(1, 0.2*cm))

    for line in make_code_block(
        "# Datei speichern: Strg+O → Enter → Strg+X\n"
        "sudo netplan apply\n"
        "# Prüfen:\nip addr show", styles):
        story.append(line)
    story.append(Spacer(1, 0.3*cm))

    story.append(make_step_box("B", "Hostname setzen", styles))
    story.append(Spacer(1, 0.15*cm))
    for line in make_code_block(
        "sudo hostnamectl set-hostname server.gruppe4.local\n"
        "echo '172.16.40.10  server.gruppe4.local server' | sudo tee -a /etc/hosts",
        styles):
        story.append(line)
    story.append(Spacer(1, 0.3*cm))

    story.append(make_step_box("C", "System aktualisieren", styles))
    story.append(Spacer(1, 0.15*cm))
    for line in make_code_block(
        "sudo apt update && sudo apt upgrade -y",
        styles):
        story.append(line)
    story.append(PageBreak())

    # ===================== KAPITEL 4: SSH =====================
    story.append(Paragraph("4. SSH-Server konfigurieren", styles['h2']))
    story.append(HRFlowable(width=W, thickness=2, color=MED_BLUE))
    story.append(Spacer(1, 0.2*cm))

    story.append(make_step_box("1", "SSH-Server installieren", styles))
    story.append(Spacer(1, 0.15*cm))
    for line in make_code_block(
        "sudo apt install openssh-server -y\n"
        "sudo systemctl status ssh    # Prüfen ob aktiv",
        styles):
        story.append(line)
    story.append(Spacer(1, 0.3*cm))

    story.append(make_step_box("2", "SSH-Konfiguration anpassen", styles))
    story.append(Spacer(1, 0.15*cm))
    for line in make_code_block(
        "sudo nano /etc/ssh/sshd_config",
        styles):
        story.append(line)
    story.append(Spacer(1, 0.2*cm))

    story.append(Paragraph("Wichtige Einstellungen prüfen/ändern:", styles['h4']))
    ssh_config = [
        ['Einstellung', 'Wert', 'Bedeutung'],
        ['Port', '22', 'Standard SSH-Port'],
        ['PermitRootLogin', 'no', 'Root-Login verbieten (Sicherheit!)'],
        ['PasswordAuthentication', 'yes', 'Passwort-Login erlauben'],
        ['AllowUsers', '*@172.16.40.*', 'Nur internes Netzwerk'],
    ]
    story.append(make_info_table(ssh_config, [4.5*cm, 4*cm, 7*cm]))
    story.append(Spacer(1, 0.3*cm))

    story.append(make_step_box("3", "SSH-Banner erstellen", styles))
    story.append(Spacer(1, 0.15*cm))
    for line in make_code_block(
        "sudo nano /etc/ssh/banner",
        styles):
        story.append(line)
    story.append(Spacer(1, 0.1*cm))
    story.append(Paragraph("Inhalt:", styles['h4']))
    for line in make_code_block(
        "====================================================\n"
        " Müller & Partner GmbH - Internes Serversystem\n"
        " Server: server.gruppe4.local (172.16.40.10)\n"
        " Nur autorisierter Zugriff!\n"
        "====================================================",
        styles):
        story.append(line)
    story.append(Spacer(1, 0.2*cm))

    story.append(Paragraph(
        "In sshd_config die Banner-Zeile hinzufügen: Banner /etc/ssh/banner",
        styles['note']
    ))
    story.append(Spacer(1, 0.3*cm))

    story.append(make_step_box("4", "SSH neu starten und aktivieren", styles))
    story.append(Spacer(1, 0.15*cm))
    for line in make_code_block(
        "sudo systemctl restart ssh\n"
        "sudo systemctl enable ssh\n"
        "# Status prüfen:\nsudo systemctl status ssh",
        styles):
        story.append(line)
    story.append(Spacer(1, 0.3*cm))

    story.append(make_step_box("5", "SSH-Verbindung testen (vom Client aus)", styles))
    story.append(Spacer(1, 0.15*cm))
    for line in make_code_block(
        "# Auf dem Client ausführen:\nssh admin@172.16.40.10\n"
        "# oder mit Hostname:\nssh admin@server.gruppe4.local",
        styles):
        story.append(line)
    story.append(Spacer(1, 0.2*cm))

    ok_box = Table([[Paragraph(
        "✅ Erfolgreich: Du siehst den Banner und wirst nach dem Passwort gefragt.",
        styles['success']
    )]], colWidths=[W])
    ok_box.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#e8f5e9')),
        ('BOX', (0, 0), (-1, -1), 1.5, GREEN_OK),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(ok_box)
    story.append(PageBreak())

    # ===================== KAPITEL 5: APACHE =====================
    story.append(Paragraph("5. Apache Webserver installieren", styles['h2']))
    story.append(HRFlowable(width=W, thickness=2, color=MED_BLUE))
    story.append(Spacer(1, 0.2*cm))

    story.append(make_step_box("1", "Apache installieren", styles))
    story.append(Spacer(1, 0.15*cm))
    for line in make_code_block(
        "sudo apt install apache2 -y\n"
        "sudo systemctl status apache2",
        styles):
        story.append(line)
    story.append(Spacer(1, 0.3*cm))

    story.append(make_step_box("2", "Webseite (index.html) erstellen", styles))
    story.append(Spacer(1, 0.15*cm))
    for line in make_code_block(
        "sudo nano /var/www/html/index.html",
        styles):
        story.append(line)
    story.append(Spacer(1, 0.1*cm))
    story.append(Paragraph("Beispiel-Inhalt für eine einfache Intranet-Seite:", styles['h4']))
    for line in make_code_block(
        "<!DOCTYPE html>\n<html lang='de'>\n<head>\n"
        "    <meta charset='UTF-8'>\n"
        "    <title>Müller & Partner - Intranet</title>\n</head>\n"
        "<body>\n"
        "    <h1>Willkommen im Intranet</h1>\n"
        "    <p>Müller &amp; Partner GmbH - Gruppe 4</p>\n"
        "    <p>Server: server.gruppe4.local | IP: 172.16.40.10</p>\n"
        "</body>\n</html>",
        styles):
        story.append(line)
    story.append(Spacer(1, 0.3*cm))

    story.append(make_step_box("3", "Apache aktivieren und starten", styles))
    story.append(Spacer(1, 0.15*cm))
    for line in make_code_block(
        "sudo systemctl enable apache2\n"
        "sudo systemctl restart apache2\n"
        "# Prüfen:\nsudo systemctl status apache2",
        styles):
        story.append(line)
    story.append(Spacer(1, 0.3*cm))

    story.append(make_step_box("4", "Webserver testen (auf dem Server selbst)", styles))
    story.append(Spacer(1, 0.15*cm))
    for line in make_code_block(
        "curl http://localhost\n"
        "# oder:\ncurl http://172.16.40.10",
        styles):
        story.append(line)
    story.append(Spacer(1, 0.2*cm))

    story.append(Paragraph(
        "ℹ️ Die Webseite im Repository enthält bereits eine fertige professionelle Intranet-Seite. "
        "Diese kann direkt aus dem GitHub-Repository heruntergeladen werden.",
        styles['note']
    ))
    story.append(Spacer(1, 0.3*cm))

    story.append(make_step_box("5", "Apache-Logs anzeigen (für Dokumentation)", styles))
    story.append(Spacer(1, 0.15*cm))
    for line in make_code_block(
        "# Access-Log (zeigt alle Zugriffe):\nsudo tail -f /var/log/apache2/access.log\n\n"
        "# Error-Log:\nsudo tail -f /var/log/apache2/error.log",
        styles):
        story.append(line)
    story.append(PageBreak())

    # ===================== KAPITEL 6: FIREWALL =====================
    story.append(Paragraph("6. Firewall (UFW) einrichten", styles['h2']))
    story.append(HRFlowable(width=W, thickness=2, color=MED_BLUE))
    story.append(Spacer(1, 0.2*cm))

    story.append(Paragraph(
        "UFW (Uncomplicated Firewall) schützt den Server. "
        "Wir erlauben nur SSH (Port 22) und HTTP (Port 80):",
        styles['body']
    ))
    story.append(Spacer(1, 0.2*cm))

    for line in make_code_block(
        "# UFW installieren (meist vorinstalliert):\nsudo apt install ufw -y\n\n"
        "# Standard: alles ABLEHNEN\nsudo ufw default deny incoming\n"
        "sudo ufw default allow outgoing\n\n"
        "# Nur SSH und HTTP ERLAUBEN:\nsudo ufw allow 22/tcp     # SSH\n"
        "sudo ufw allow 80/tcp     # HTTP Webserver\n\n"
        "# Firewall AKTIVIEREN:\nsudo ufw enable\n\n"
        "# Status anzeigen:\nsudo ufw status verbose",
        styles):
        story.append(line)
    story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph("Erwartete Ausgabe von 'sudo ufw status verbose':", styles['h4']))
    for line in make_code_block(
        "Status: active\nLogging: on (low)\nDefault: deny (incoming), allow (outgoing)\n\n"
        "To                         Action      From\n"
        "--                         ------      ----\n"
        "22/tcp                     ALLOW IN    Anywhere\n"
        "80/tcp                     ALLOW IN    Anywhere",
        styles):
        story.append(line)
    story.append(Spacer(1, 0.3*cm))

    fw_table = [
        ['Firewall-Regel', 'Port', 'Protokoll', 'Aktion', 'Begründung'],
        ['SSH', '22', 'TCP', 'ALLOW', 'Fernadministration des Servers'],
        ['HTTP', '80', 'TCP', 'ALLOW', 'Webserver / Intranet-Zugriff'],
        ['Alles andere', '*', '*', 'DENY', 'Sicherheit - nicht benötigt'],
    ]
    fw_t = Table(fw_table, colWidths=[3*cm, 2*cm, 2.5*cm, 2.5*cm, 5.5*cm])
    fw_t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), DARK_BLUE),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, LIGHT_GRAY]),
        ('TEXTCOLOR', (3, 1), (3, 2), GREEN_OK),
        ('TEXTCOLOR', (3, 3), (3, 3), RED_ERR),
        ('FONTNAME', (3, 1), (3, -1), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 0.5, MED_GRAY),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(fw_t)
    story.append(PageBreak())

    # ===================== KAPITEL 7: CLIENT =====================
    story.append(Paragraph("7. Client-VM einrichten", styles['h2']))
    story.append(HRFlowable(width=W, thickness=2, color=MED_BLUE))
    story.append(Spacer(1, 0.2*cm))

    story.append(Paragraph(
        "Für den Client empfehlen wir Ubuntu Desktop. Alternativ reicht auch Ubuntu Server.",
        styles['body']
    ))
    story.append(Spacer(1, 0.2*cm))

    story.append(make_step_box("🚀", "SCHNELLE METHODE: Automatisches Client-Setup (Empfohlen!)", styles))
    story.append(Spacer(1, 0.15*cm))
    story.append(Paragraph(
        "Statt das Netzwerk manuell zu konfigurieren, kannst du das Client-Automatisierungsskript "
        "direkt in der Client-VM ausführen:",
        styles['body']
    ))
    for line in make_code_block(
        "# Client-VM vollautomatisch einrichten (IP 172.16.40.100, Hosts-Eintrag, Wireshark):\n"
        "curl -sSL https://raw.githubusercontent.com/kluthjan/uwearbeit/main/scripts/client_setup.sh | sudo bash",
        styles):
        story.append(line)
    story.append(Spacer(1, 0.3*cm))

    story.append(make_step_box("1", "MANUELLE METHODE: Client-Netzwerk konfigurieren", styles))
    story.append(Spacer(1, 0.15*cm))
    story.append(Paragraph(
        "Gleiches Vorgehen wie beim Server, aber mit Client-IP 172.16.40.100:",
        styles['body']
    ))
    for line in make_code_block(
        "sudo nano /etc/netplan/00-installer-config.yaml\n\n"
        "# Inhalt:\nnetwork:\n  version: 2\n  renderer: networkd\n  ethernets:\n"
        "    enp0s3:         # <-- Deinen Interface-Namen eintragen!\n"
        "      addresses:\n        - 172.16.40.100/24\n"
        "      routes:\n        - to: default\n          via: 172.16.40.1\n"
        "      nameservers:\n        addresses: [172.16.40.10, 8.8.8.8]\n"
        "      dhcp4: false\n\nsudo netplan apply",
        styles):
        story.append(line)
    story.append(Spacer(1, 0.3*cm))

    story.append(make_step_box("2", "Server in /etc/hosts eintragen", styles))
    story.append(Spacer(1, 0.15*cm))
    for line in make_code_block(
        "echo '172.16.40.10  server.gruppe4.local intranet.gruppe4.local' | sudo tee -a /etc/hosts",
        styles):
        story.append(line)
    story.append(Spacer(1, 0.3*cm))

    story.append(make_step_box("3", "Verbindung zum Server testen", styles))
    story.append(Spacer(1, 0.15*cm))
    for line in make_code_block(
        "# Netzwerk testen:\nping -c 4 172.16.40.10\n\n"
        "# SSH-Port testen:\nnc -zv 172.16.40.10 22\n\n"
        "# Webserver testen:\ncurl http://172.16.40.10",
        styles):
        story.append(line)
    story.append(PageBreak())

    # ===================== KAPITEL 8: SSH VOM CLIENT =====================
    story.append(Paragraph("8. SSH-Verbindung vom Client herstellen", styles['h2']))
    story.append(HRFlowable(width=W, thickness=2, color=MED_BLUE))
    story.append(Spacer(1, 0.2*cm))

    story.append(make_step_box("1", "SSH-Verbindung herstellen", styles))
    story.append(Spacer(1, 0.15*cm))
    for line in make_code_block(
        "# Auf dem CLIENT ausführen:\nssh admin@172.16.40.10\n\n"
        "# Beim ersten Verbinden: 'yes' eingeben und Enter drücken\n"
        "# Dann Passwort eingeben: Admin1234!\n\n"
        "# Mit Hostname (nach /etc/hosts Eintrag):\nssh admin@server.gruppe4.local",
        styles):
        story.append(line)
    story.append(Spacer(1, 0.3*cm))

    story.append(make_step_box("2", "SSH-Schlüssel generieren (sicherere Methode)", styles))
    story.append(Spacer(1, 0.15*cm))
    story.append(Paragraph(
        "Statt Passwort kann man einen SSH-Schlüssel verwenden (sicherer):",
        styles['body']
    ))
    for line in make_code_block(
        "# Auf dem CLIENT:\n"
        "ssh-keygen -t rsa -b 4096 -C 'gruppe4-client'\n"
        "# → Enter drücken für Standardpfad\n"
        "# → Passphrase: leer lassen (Enter) oder Passwort setzen\n\n"
        "# Schlüssel auf Server kopieren:\nssh-copy-id admin@172.16.40.10\n"
        "# Passwort eingeben: Admin1234!\n\n"
        "# Ab jetzt ohne Passwort verbinden:\nssh admin@172.16.40.10",
        styles):
        story.append(line)
    story.append(Spacer(1, 0.3*cm))

    story.append(make_step_box("3", "Webserver über SSH verwalten", styles))
    story.append(Spacer(1, 0.15*cm))
    story.append(Paragraph(
        "Nach der SSH-Verbindung kann der Webserver vom Client aus administriert werden:",
        styles['body']
    ))
    for line in make_code_block(
        "# SSH-Verbindung herstellen:\nssh admin@172.16.40.10\n\n"
        "# Webseite bearbeiten:\nsudo nano /var/www/html/index.html\n\n"
        "# Apache neu starten:\nsudo systemctl restart apache2\n\n"
        "# Apache-Status prüfen:\nsudo systemctl status apache2\n\n"
        "# Logs anzeigen:\nsudo tail -f /var/log/apache2/access.log",
        styles):
        story.append(line)
    story.append(PageBreak())

    # ===================== KAPITEL 9: BROWSER =====================
    story.append(Paragraph("9. Webseite über Browser öffnen", styles['h2']))
    story.append(HRFlowable(width=W, thickness=2, color=MED_BLUE))
    story.append(Spacer(1, 0.2*cm))

    story.append(Paragraph(
        "Auf dem Client-Desktop (mit grafischer Oberfläche) kann die Intranet-Webseite im Browser "
        "geöffnet werden:",
        styles['body']
    ))
    story.append(Spacer(1, 0.2*cm))

    browser_steps = [
        ['Via IP-Adresse:', 'http://172.16.40.10', 'Direkte IP-Adresse des Servers'],
        ['Via Hostname:', 'http://server.gruppe4.local', 'Nach /etc/hosts Eintrag'],
        ['Via Alias:', 'http://intranet.gruppe4.local', 'Alternativer Hostname'],
    ]
    browser_t = Table(browser_steps, colWidths=[4*cm, 6*cm, 6.5*cm])
    browser_t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), DARK_BLUE),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Courier-Bold'),
        ('TEXTCOLOR', (1, 0), (1, -1), MED_BLUE),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, LIGHT_GRAY]),
        ('GRID', (0, 0), (-1, -1), 0.5, MED_GRAY),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(browser_t)
    story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph("Browser installieren (falls nicht vorhanden):", styles['h4']))
    for line in make_code_block(
        "sudo apt install firefox-esr -y\n"
        "# oder:\nsudo apt install chromium-browser -y",
        styles):
        story.append(line)
    story.append(PageBreak())

    # ===================== KAPITEL 10: WIRESHARK =====================
    story.append(Paragraph("10. Netzwerkanalyse mit Wireshark", styles['h2']))
    story.append(HRFlowable(width=W, thickness=2, color=MED_BLUE))
    story.append(Spacer(1, 0.2*cm))

    story.append(make_step_box("1", "Wireshark installieren", styles))
    story.append(Spacer(1, 0.15*cm))
    for line in make_code_block(
        "sudo apt install wireshark -y\n"
        "# Frage 'darf Wireshark als normaler Benutzer laufen?' → YES\n"
        "sudo usermod -aG wireshark $USER\n"
        "# Abmelden und neu anmelden!",
        styles):
        story.append(line)
    story.append(Spacer(1, 0.3*cm))

    story.append(make_step_box("2", "HTTP-Verkehr mitschneiden", styles))
    story.append(Spacer(1, 0.15*cm))
    story.append(Paragraph("Mit Wireshark (grafisch):", styles['h4']))
    wireshark_steps = [
        "Wireshark starten: sudo wireshark",
        "Netzwerk-Interface auswählen (z.B. enp0s3)",
        "Filter eingeben: tcp.port == 80",
        "Start-Button klicken (blaues Haifisch-Symbol)",
        "Auf dem Client im Browser die Webseite aufrufen: http://172.16.40.10",
        "Pakete beobachten!",
    ]
    for i, s in enumerate(wireshark_steps, 1):
        story.append(Paragraph(f"<b>{i}.</b> {s}", styles['bullet']))
    story.append(Spacer(1, 0.2*cm))

    story.append(Paragraph("Mit tcpdump (Terminal, für Screenshot/Dokumentation):", styles['h4']))
    for line in make_code_block(
        "# HTTP-Verkehr beobachten:\nsudo tcpdump -i enp0s3 port 80 -v\n\n"
        "# SSH-Verkehr beobachten:\nsudo tcpdump -i enp0s3 port 22 -v\n\n"
        "# Alle Pakete vom Server:\nsudo tcpdump -i enp0s3 host 172.16.40.10 -v",
        styles):
        story.append(line)
    story.append(PageBreak())

    # ===================== KAPITEL 11: FUNKTIONSTESTS =====================
    story.append(Paragraph("11. Funktionstests & Dokumentation", styles['h2']))
    story.append(HRFlowable(width=W, thickness=2, color=MED_BLUE))
    story.append(Spacer(1, 0.2*cm))

    story.append(Paragraph("Checkliste – alle Tests durchführen und Screenshots machen:", styles['h3']))
    tests = [
        ['☐', 'Server-IP konfiguriert', 'ip addr show → 172.16.40.10 sichtbar'],
        ['☐', 'Client-IP konfiguriert', 'ip addr show → 172.16.40.100 sichtbar'],
        ['☐', 'Ping Server → Client', 'ping 172.16.40.100 (vom Server)'],
        ['☐', 'Ping Client → Server', 'ping 172.16.40.10 (vom Client)'],
        ['☐', 'SSH-Verbindung', 'ssh admin@172.16.40.10 → Login erfolgreich'],
        ['☐', 'SSH-Banner sichtbar', 'Banner erscheint beim Login'],
        ['☐', 'Webserver läuft', 'systemctl status apache2 → active'],
        ['☐', 'Browser zeigt Webseite', 'http://172.16.40.10 im Browser'],
        ['☐', 'Firewall aktiv', 'sudo ufw status verbose'],
        ['☐', 'Wireshark: HTTP-Pakete', 'HTTP-Anfrage in Wireshark sichtbar'],
        ['☐', 'Webseite via SSH ändern', 'Änderung via SSH → Webseite aktualisiert'],
        ['☐', 'Apache-Log Zugriffe', 'tail /var/log/apache2/access.log'],
    ]
    test_t = Table(tests, colWidths=[0.8*cm, 5*cm, 10*cm])
    test_t.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (0, -1), 14),
        ('TEXTCOLOR', (0, 0), (0, -1), ORANGE_WARN),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, -1), 'Courier'),
        ('FONTSIZE', (2, 0), (2, -1), 8),
        ('TEXTCOLOR', (2, 0), (2, -1), DARK_GRAY),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, LIGHT_GRAY]),
        ('GRID', (0, 0), (-1, -1), 0.3, MED_GRAY),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(test_t)
    story.append(PageBreak())

    # ===================== KAPITEL 12: PROBLEME =====================
    story.append(Paragraph("12. Häufige Probleme & Lösungen", styles['h2']))
    story.append(HRFlowable(width=W, thickness=2, color=MED_BLUE))
    story.append(Spacer(1, 0.2*cm))

    problems = [
        ("❌ SSH-Verbindung wird abgelehnt",
         "sudo systemctl restart ssh\nsudo systemctl status ssh\n# Prüfe Firewall:\nsudo ufw status"),
        ("❌ Webseite nicht erreichbar",
         "sudo systemctl restart apache2\nsudo systemctl status apache2\n# Port prüfen:\nss -tlnp | grep :80"),
        ("❌ Ping funktioniert nicht",
         "# Netzwerkkonfiguration prüfen:\nip addr show\n# Interface prüfen:\nip route show\n# Netzwerkname in VirtualBox korrekt?"),
        ("❌ 'Permission denied' bei SSH",
         "# Benutzer existiert?\nid admin\n# SSH-Config prüfen:\nsudo grep PasswordAuthentication /etc/ssh/sshd_config"),
        ("❌ netplan apply schlägt fehl",
         "# YAML-Syntax prüfen (Einrückungen!):\nsudo netplan --debug apply\n# Tabs statt Spaces? → Spaces verwenden!"),
    ]
    for prob, sol in problems:
        story.append(Paragraph(f"<b>{prob}</b>", styles['h4']))
        story.append(Paragraph("Lösung:", styles['body']))
        for line in make_code_block(sol, styles):
            story.append(line)
        story.append(Spacer(1, 0.3*cm))

    story.append(Spacer(1, 0.5*cm))
    final_box = Table([[Paragraph(
        "🎉 Viel Erfolg bei der Präsentation!\n\n"
        "GitHub: https://github.com/kluthjan/uwearbeit\n"
        "Team: Jan, Marian, Mathias, Marco | Gruppe 4\n"
        "Netzwerk: 172.16.40.0/24 | Server: 172.16.40.10",
        ParagraphStyle('Final', fontName='Helvetica-Bold', fontSize=12,
                       textColor=colors.white, alignment=TA_CENTER)
    )]], colWidths=[W])
    final_box.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), DARK_BLUE),
        ('TOPPADDING', (0, 0), (-1, -1), 20),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 20),
    ]))
    story.append(final_box)

    doc.build(story)
    print(f"✅ Team-Anleitung erstellt: {path}")
    return path


# =============================================================================
# DOKUMENT 2: PROJEKTDOKUMENTATION
# =============================================================================
def create_project_documentation():
    """Create the project documentation PDF."""
    path = os.path.join(OUT_DIR, "Projektdokumentation_Gruppenarbeit4.pdf")
    styles = get_styles()

    def header_footer(c, d):
        page_header_footer(c, d, "Projektdokumentation")

    doc = SimpleDocTemplate(
        path, pagesize=A4,
        leftMargin=1.8*cm, rightMargin=1.8*cm,
        topMargin=2.5*cm, bottomMargin=2*cm,
        onFirstPage=header_footer, onLaterPages=header_footer
    )

    story = []
    W = A4[0] - 3.6*cm

    # Titelseite
    tb = Table([[Paragraph(
        "PROJEKTDOKUMENTATION<br/><font size='16'>Gruppenarbeit 4</font><br/>"
        "<font size='14'>Webserver mit SSH-Fernadministration</font>",
        styles['title_page']
    )]], colWidths=[W])
    tb.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), DARK_BLUE),
        ('TOPPADDING', (0, 0), (-1, -1), 30), ('BOTTOMPADDING', (0, 0), (-1, -1), 30),
    ]))
    story.append(tb)
    story.append(Spacer(1, 0.5*cm))

    meta = [
        ['Projekt', 'Gruppenarbeit 4 – IT-Systeme'],
        ['Thema', 'Webserver mit SSH-Fernadministration'],
        ['Team (Gruppe 4)', 'Jan (Leiter), Marian, Mathias, Marco'],
        ['Auftraggeber', 'Müller & Partner GmbH (fiktiv)'],
        ['Netzwerk', '172.16.40.0/24'],
        ['Server', '172.16.40.10 (server.gruppe4.local)'],
        ['Client', '172.16.40.100 (client.gruppe4.local)'],
        ['Datum', '2026'],
    ]
    mt = Table(meta, colWidths=[5*cm, 10.5*cm])
    mt.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'), ('TEXTCOLOR', (0, 0), (0, -1), MED_BLUE),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'), ('ROWBACKGROUNDS', (0, 0), (-1, -1), [LIGHT_GRAY, colors.white]),
        ('GRID', (0, 0), (-1, -1), 0.5, MED_GRAY), ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 6), ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(mt)
    story.append(PageBreak())

    # Wasserfallmodell-Phasen
    phases = [
        ("1. Projektinitiierung", [
            ("Ausgangssituation", "Die Müller & Partner GmbH möchte ein internes Intranet für ihre Mitarbeiter bereitstellen. Informationen, Ankündigungen und interne Hinweise sollen zentral veröffentlicht werden. Der Server soll über SSH fernadministriert werden können."),
            ("Kundenauftrag", "Installation und Konfiguration eines Webservers (Apache HTTP) und SSH-Servers (OpenSSH) in einer virtualisierten Umgebung (VirtualBox). Einrichtung einer Firewall (UFW). Client soll Webseite im Browser aufrufen und per SSH administrieren können."),
            ("Zieldefinition", "✓ Apache Webserver läuft auf 172.16.40.10:80\n✓ SSH-Server läuft auf 172.16.40.10:22\n✓ Client kann Webseite im Browser öffnen\n✓ Client kann per SSH den Server administrieren\n✓ Firewall erlaubt nur Port 22 und 80"),
        ]),
        ("2. Projektplanung", [
            ("Netzwerkkonzept", "Netzwerk: 172.16.40.0/24\nServer: 172.16.40.10 (static)\nClient: 172.16.40.100 (static)\nGateway: 172.16.40.1\nVirtualBox: Internes Netzwerk 'intnet-gruppe4'"),
            ("Zeitplanung", "Tag 1: VMs einrichten, Netzwerk konfigurieren\nTag 2: SSH und Apache installieren\nTag 3: Firewall, Tests, Wireshark\nTag 4: Dokumentation und Präsentation"),
            ("Ressourcen", "Software: VirtualBox, Ubuntu Server 22.04, Ubuntu Desktop 22.04\nDienste: OpenSSH-Server, Apache2, UFW\nTools: Wireshark, tcpdump, curl"),
        ]),
        ("3. Projektdurchführung", [
            ("Server-VM einrichten", "Ubuntu Server 22.04 LTS installiert, statische IP 172.16.40.10 über Netplan konfiguriert, Hostname 'server.gruppe4.local' gesetzt."),
            ("SSH-Server", "OpenSSH-Server installiert und konfiguriert. PermitRootLogin=no, PasswordAuthentication=yes, AllowUsers nur aus 172.16.40.0/24. SSH-Banner erstellt."),
            ("Apache Webserver", "Apache2 installiert. Intranet-Startseite unter /var/www/html/index.html erstellt. Webseite enthält Firmeninformationen, Ankündigungen und Serverinformationen."),
            ("Firewall UFW", "UFW installiert. Standard-Policy: deny incoming, allow outgoing. Eingehend erlaubt: Port 22 (SSH) und Port 80 (HTTP). Alle anderen Ports geblockt."),
            ("Client-VM", "Ubuntu Desktop eingerichtet, statische IP 172.16.40.100. Server in /etc/hosts eingetragen. SSH-Schlüsselpaar generiert."),
        ]),
        ("4. Projektabschluss", [
            ("Ergebnisse", "Alle Ziele wurden erreicht:\n✅ SSH-Verbindung vom Client zum Server funktioniert\n✅ Webseite im Browser des Clients erreichbar\n✅ Webserver kann per SSH administriert werden\n✅ Firewall aktiv und korrekt konfiguriert\n✅ Netzwerkanalyse mit Wireshark durchgeführt"),
            ("Lessons Learned", "• Netplan YAML-Syntax ist einrückungssensitiv (Spaces, keine Tabs)\n• VirtualBox-Netzwerkname muss bei BEIDEN VMs identisch sein\n• Firewall-Regeln vor dem Aktivieren prüfen (SSH nicht ausperren!)\n• Apache-Logs helfen bei der Fehlersuche"),
            ("Sicherheitsaspekte in der Produktion", "In einer echten Produktionsumgebung würde man:\n• HTTPS statt HTTP verwenden (TLS-Zertifikat)\n• SSH-Schlüsselauthentifizierung statt Passwort\n• Fail2Ban gegen Brute-Force-Angriffe\n• Regelmäßige Sicherheitsupdates\n• VPN für Fernzugriff"),
        ]),
    ]

    for phase_title, sections in phases:
        story.append(Paragraph(phase_title, styles['h2']))
        story.append(HRFlowable(width=W, thickness=2, color=MED_BLUE))
        story.append(Spacer(1, 0.2*cm))
        for sec_title, sec_content in sections:
            story.append(Paragraph(sec_title, styles['h3']))
            story.append(Paragraph(sec_content.replace('\n', '<br/>'), styles['body']))
            story.append(Spacer(1, 0.2*cm))
        story.append(Spacer(1, 0.3*cm))

    doc.build(story)
    print(f"✅ Projektdokumentation erstellt: {path}")
    return path


# =============================================================================
# DOKUMENT 3: PROJEKTPLAN (kurz, für Team)
# =============================================================================
def create_project_plan():
    """Create a project plan PDF."""
    path = os.path.join(OUT_DIR, "Projektplan_Gruppenarbeit4.pdf")
    styles = get_styles()

    def header_footer(c, d):
        page_header_footer(c, d, "Projektplan")

    doc = SimpleDocTemplate(path, pagesize=A4,
        leftMargin=1.8*cm, rightMargin=1.8*cm,
        topMargin=2.5*cm, bottomMargin=2*cm,
        onFirstPage=header_footer, onLaterPages=header_footer)

    story = []
    W = A4[0] - 3.6*cm

    tb = Table([[Paragraph(
        "PROJEKTPLAN<br/><font size='14'>Gruppenarbeit 4 – SSH &amp; Webserver</font>",
        styles['title_page']
    )]], colWidths=[W])
    tb.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), DARK_BLUE),
        ('TOPPADDING', (0, 0), (-1, -1), 25), ('BOTTOMPADDING', (0, 0), (-1, -1), 25),
    ]))
    story.append(tb)
    story.append(Spacer(1, 0.5*cm))

    story.append(Paragraph("Aufgabenverteilung – Gruppe 4", styles['h2']))
    tasks = [
        ['Aufgabe', 'Verantwortlich', 'Status'],
        ['VMs in VirtualBox einrichten', 'Jan', '○ Offen'],
        ['Netzwerk Server konfigurieren', 'Marian', '○ Offen'],
        ['Netzwerk Client konfigurieren', 'Marco', '○ Offen'],
        ['SSH-Server installieren & konfigurieren', 'Mathias', '○ Offen'],
        ['Apache Webserver installieren', 'Jan', '○ Offen'],
        ['Intranet-Webseite gestalten', 'Marco', '○ Offen'],
        ['Firewall (UFW) einrichten', 'Marian', '○ Offen'],
        ['SSH-Verbindung testen', 'Alle', '○ Offen'],
        ['Wireshark-Analyse durchführen', 'Mathias', '○ Offen'],
        ['Projektdokumentation schreiben', 'Jan + Marian', '○ Offen'],
        ['Präsentation erstellen', 'Marco + Mathias', '○ Offen'],
        ['Präsentation üben', 'Alle', '○ Offen'],
    ]
    tt = Table(tasks, colWidths=[8*cm, 4*cm, 3.5*cm])
    tt.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), DARK_BLUE), ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'), ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, LIGHT_GRAY]),
        ('GRID', (0, 0), (-1, -1), 0.5, MED_GRAY), ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('TOPPADDING', (0, 0), (-1, -1), 5), ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(tt)
    story.append(Spacer(1, 0.5*cm))

    story.append(Paragraph("Zeitplan (Schätzung)", styles['h2']))
    timeline = [
        ['Phase', 'Aktivitäten', 'Dauer'],
        ['Phase 1', 'VMs einrichten, Netzwerk konfigurieren', '1-2 Stunden'],
        ['Phase 2', 'SSH + Apache installieren, testen', '1-2 Stunden'],
        ['Phase 3', 'Firewall, Wireshark, Dokumentation', '1-2 Stunden'],
        ['Phase 4', 'Präsentation erstellen und üben', '1 Stunde'],
    ]
    tl = Table(timeline, colWidths=[3*cm, 10*cm, 3*cm])
    tl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), DARK_BLUE), ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'), ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, LIGHT_GRAY]),
        ('GRID', (0, 0), (-1, -1), 0.5, MED_GRAY), ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('TOPPADDING', (0, 0), (-1, -1), 5), ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(tl)

    doc.build(story)
    print(f"✅ Projektplan erstellt: {path}")
    return path


# =============================================================================
# MAIN
# =============================================================================
if __name__ == "__main__":
    print("=" * 60)
    print("PDF-Generator für Gruppenarbeit 4")
    print("Gruppe 4: Jan, Marian, Mathias, Marco")
    print("=" * 60)

    paths = []
    try:
        paths.append(create_team_guide())
        paths.append(create_project_documentation())
        paths.append(create_project_plan())

        print("\n" + "=" * 60)
        print("✅ ALLE PDFs erfolgreich erstellt:")
        for p in paths:
            print(f"   📄 {p}")
        print("=" * 60)
    except Exception as e:
        print(f"❌ Fehler: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

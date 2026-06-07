import os
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.lib.colors import HexColor, white, black
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle,
    Image, HRFlowable, KeepTogether
)
from reportlab.platypus.flowables import Flowable

# ── Path Configuration ────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")
OUTPUT_PDF = os.path.join(BASE_DIR, "customer_segmentation_report.pdf")

# Read association rules dynamically from outputs/ directory
top_rules = {}
for i in range(5):
    rule_path = os.path.join(OUTPUTS_DIR, f"rules_cluster_{i}.csv")
    if os.path.exists(rule_path):
        try:
            df_rules = pd.read_csv(rule_path).head(3)
            # Assuming columns: antecedents_str, consequents_str, support, confidence, lift
            rules_list = df_rules[['antecedents_str', 'consequents_str', 'support', 'confidence', 'lift']].values.tolist()
            top_rules[str(i)] = rules_list
        except Exception as e:
            print(f"Warning: Could not parse {rule_path} - {e}")

W, H = A4
MARGIN = 2.0 * cm

NAVY    = HexColor("#0b1929")
BLUE    = HexColor("#2563eb")
BLUE_LT = HexColor("#dbeafe")
GREY_LT = HexColor("#f1f5f9")
GREY    = HexColor("#64748b")
DARK    = HexColor("#1e293b")
LINE    = HexColor("#e2e8f0")
WHITE   = white

C_EDA  = HexColor("#16a34a")
C_CLUS = HexColor("#7c3aed")
C_CAMP = HexColor("#d97706")
C_CONC = HexColor("#0891b2")

SEG_HEX = {0:HexColor("#4f8ef7"),1:HexColor("#f87171"),2:HexColor("#34c97a"),3:HexColor("#a78bfa"),4:HexColor("#f59e0b")}
SEG_NAMES = {0:"Tech-Savvy Singles",1:"Budget-Conscious Shoppers",2:"Core Everyday Shoppers",3:"High-Value Families",4:"Pet and Home Essentials"}
SEG_STATS = {
    0:("3,323","10.1%","EUR 23,741","54.6 yrs","0.6","6.7 yrs"),
    1:("2,337","7.1%","EUR 10,602","56.6 yrs","1.8","9.4 yrs"),
    2:("13,460","40.7%","EUR 19,247","49.3 yrs","1.5","8.0 yrs"),
    3:("6,942","21.0%","EUR 42,729","56.1 yrs","3.8","11.1 yrs"),
    4:("6,976","21.1%","EUR 17,321","55.5 yrs","1.9","8.3 yrs"),
}
SEG_DESC = {
    0:"These customers spend heavily on electronics and video games, have almost no children at home, and visit fewer stores than average. Despite lower visit frequency, they are high-value per visit.",
    1:"The most price-sensitive segment. They spread their spend across the highest number of distinct stores, indicating active cross-shopping behaviour.",
    2:"The backbone of the customer base at 41% of all customers. Grocery and fresh produce are the dominant categories, with broad product diversity.",
    3:"The most profitable and loyal segment. Large households, the longest customer tenure, and spend spread across every category.",
    4:"Characterised by consistent, predictable pet-food and hygiene purchases. Very low penetration in meat and fish.",
}
SEG_CHARS = {
    0:["Highest electronics and video-game lifetime spend","Fewest children at home (avg 0.6)","Below-average store visit count"],
    1:["Lowest average lifetime spend (EUR 10,602)","Highest number of distinct stores visited","Above-average promotional purchase rate"],
    2:["Largest segment: 40.7% of the customer base","Grocery and vegetables are dominant spend categories","Moderate age (49.3 yrs) and tenure (8.0 yrs)"],
    3:["Highest average lifetime spend: EUR 42,729","Largest household size (avg 3.8 children)","Longest customer tenure (11.1 yrs)"],
    4:["Highest pet-food and hygiene spend","Very low meat and fish penetration","Highly predictable and routine purchase patterns"],
}
SEG_CAMPAIGNS = {
    0:[("Buy 1 Video Game, get 1 free","Targets the above-average video-game spend and gaming affinity found in basket rules."),
       ("Device trade-in: get 15% off a new one","Upgrade mechanics match this segment's propensity for tech purchases.")],
    1:[("50% off the second basket item in household","Addresses the household and essentials basket patterns in this cluster."),
       ("Loyalty card double-points every Wednesday","Creates a weekly anchor visit day to consolidate cross-shopping.")],
    2:[("Get 20% off Fish when you also buy Meat","The top association rule for this cluster is a meat-to-fish co-purchase."),
       ("Weekly fresh deals: 30% off selected vegetables","Creates habitual visit cadence and deepens loyalty to the fresh produce category.")],
    3:[("Family bundle: groceries, meat and fish at 15% off","Multi-category basket composition is the defining trait of this cluster."),
       ("VIP loyalty tier: double cashback","The high average spend makes this segment the natural fit for a premium loyalty tier.")],
    4:[("Buy 2 bags of pet food, get 1 free","Pet food is the defining category of this cluster."),
       ("Subscribe and Save: 10% off recurring pet food","Routine purchase patterns make subscription conversion highly viable.")],
}

# ── Styles ────────────────────────────────────────────────────────────────────
styles = getSampleStyleSheet()
def S(base_name, **kw):
    base = styles.get(base_name, styles["Normal"])
    return ParagraphStyle(base_name+"_x"+str(id(kw)), parent=base, **kw)

title_s  = S("Title",   fontSize=26,fontName="Helvetica-Bold",textColor=NAVY,spaceAfter=6,leading=32, alignment=TA_CENTER)
subtitle_s = S("Normal", fontSize=15,fontName="Helvetica",textColor=GREY,spaceAfter=14, alignment=TA_CENTER)
h1_s     = S("Heading1",fontSize=16,fontName="Helvetica-Bold",textColor=NAVY,spaceBefore=18,spaceAfter=6,leading=20)
h2_s     = S("Heading2",fontSize=12,fontName="Helvetica-Bold",textColor=BLUE,spaceBefore=14,spaceAfter=4,leading=15)
h3_s     = S("Heading3",fontSize=10,fontName="Helvetica-Bold",textColor=DARK,spaceBefore=10,spaceAfter=3,leading=13)
body_s   = S("Normal",  fontSize=9.5,fontName="Helvetica",textColor=DARK,spaceAfter=6,leading=14,alignment=TA_JUSTIFY)
body_sm  = S("Normal",  fontSize=8.5,fontName="Helvetica",textColor=DARK,spaceAfter=4,leading=12,alignment=TA_JUSTIFY)
bullet_s = S("Normal",  fontSize=9,fontName="Helvetica",textColor=DARK,spaceAfter=3,leading=13,leftIndent=14,bulletIndent=4)
caption_s= S("Normal",  fontSize=8,fontName="Helvetica-Oblique",textColor=GREY,spaceAfter=8,alignment=TA_CENTER)
label_s  = S("Normal",  fontSize=7.5,fontName="Helvetica-Bold",textColor=GREY,spaceAfter=2)
toc_s    = S("Normal",  fontSize=10,fontName="Helvetica",textColor=DARK,spaceAfter=5,leading=14)

# Header & Student Styles
uni_s    = S("Normal",  fontSize=11,fontName="Helvetica-Bold",textColor=DARK,spaceAfter=4, alignment=TA_CENTER)
student_s= S("Normal",  fontSize=10,fontName="Helvetica",textColor=GREY,spaceAfter=3, alignment=TA_CENTER)

# ── Flowables ─────────────────────────────────────────────────────────────────
class ColorBar(Flowable):
    def __init__(self,color,height=5):
        super().__init__(); self.color=color; self._h=height
        self.width=W-2*MARGIN; self.height=height
    def draw(self):
        self.canv.setFillColor(self.color)
        self.canv.rect(0,0,self.width,self._h,fill=1,stroke=0)

class SectionHeader(Flowable):
    def __init__(self,text,color=BLUE):
        super().__init__(); self.text=text; self.color=color
        self.width=W-2*MARGIN; self.height=28
    def draw(self):
        c=self.canv
        c.setFillColor(self.color); c.roundRect(0,0,self.width,28,4,fill=1,stroke=0)
        c.setFillColor(WHITE); c.setFont("Helvetica-Bold",11.5)
        c.drawString(12,9,self.text)

class SegmentBadge(Flowable):
    def __init__(self,name,color,size,pct,avg_spend):
        super().__init__(); self.name=name; self.color=color
        self.size=size; self.pct=pct; self.avg_spend=avg_spend
        self.width=W-2*MARGIN; self.height=34
    def draw(self):
        c=self.canv
        c.setFillColor(self.color); c.rect(0,0,4,34,fill=1,stroke=0)
        c.setFillColor(HexColor("#f8fafc")); c.rect(4,0,self.width-4,34,fill=1,stroke=0)
        c.setStrokeColor(HexColor("#e2e8f0")); c.rect(4,0,self.width-4,34,fill=0,stroke=1)
        c.setFillColor(self.color); c.setFont("Helvetica-Bold",10.5); c.drawString(14,20,self.name)
        c.setFillColor(HexColor("#64748b")); c.setFont("Helvetica",8)
        c.drawString(14,7,f"{self.size} customers  |  {self.pct}  |  Avg lifetime spend {self.avg_spend}")

def img(filename, width=None):
    path = os.path.join(OUTPUTS_DIR, filename)
    if not os.path.exists(path):
        return Paragraph(f"<i>[Missing Graphic: {filename}]</i>", caption_s)
    
    i = Image(path)
    if width:
        ratio = i.imageHeight / float(i.imageWidth)
        i.drawWidth = width
        i.drawHeight = width * ratio
    return i

def bullet(text):
    return Paragraph(f"<bullet>&bull;</bullet> {text}", bullet_s)

def kv_table(rows):
    data=[[Paragraph(f"<b>{k}</b>",body_sm),Paragraph(v,body_sm)] for k,v in rows]
    cw=[(W-2*MARGIN)*0.38,(W-2*MARGIN)*0.62]
    t=Table(data,colWidths=cw)
    t.setStyle(TableStyle([
        ("ROWBACKGROUNDS",(0,0),(-1,-1),[WHITE,GREY_LT]),
        ("GRID",(0,0),(-1,-1),0.5,LINE),("VALIGN",(0,0),(-1,-1),"MIDDLE"),
        ("TOPPADDING",(0,0),(-1,-1),4),("BOTTOMPADDING",(0,0),(-1,-1),4),
        ("LEFTPADDING",(0,0),(-1,-1),8),
    ]))
    return t

def styled_table(data_rows, headers, col_widths=None, hi_col=None):
    header=[Paragraph(f"<b>{h}</b>",label_s) for h in headers]
    body=[[Paragraph(str(c),body_sm) for c in row] for row in data_rows]
    all_rows=[header]+body
    avail=W-2*MARGIN
    cw=col_widths or [avail/len(headers)]*len(headers)
    t=Table(all_rows,colWidths=cw)
    ts=[
        ("BACKGROUND",(0,0),(-1,0),NAVY),("TEXTCOLOR",(0,0),(-1,0),WHITE),
        ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),("FONTSIZE",(0,0),(-1,0),8),
        ("TOPPADDING",(0,0),(-1,0),6),("BOTTOMPADDING",(0,0),(-1,0),6),
        ("LEFTPADDING",(0,0),(-1,-1),8),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[WHITE,GREY_LT]),
        ("GRID",(0,0),(-1,-1),0.4,LINE),("VALIGN",(0,0),(-1,-1),"MIDDLE"),
        ("FONTSIZE",(0,1),(-1,-1),8.5),("TOPPADDING",(0,1),(-1,-1),4),("BOTTOMPADDING",(0,1),(-1,-1),4),
    ]
    if hi_col is not None:
        for r in range(1,len(all_rows)):
            ts+=[("TEXTCOLOR",(hi_col,r),(hi_col,r),BLUE),("FONTNAME",(hi_col,r),(hi_col,r),"Helvetica-Bold")]
    t.setStyle(TableStyle(ts)); return t

def campaign_block(campaigns,color):
    rows=[]
    for i,(title,rationale) in enumerate(campaigns,1):
        rows.append([
            Paragraph(f"<b>0{i}</b>",S("Normal",fontSize=9,fontName="Helvetica-Bold",textColor=color,alignment=TA_CENTER)),
            Paragraph(f"<b>{title}</b><br/><font size='8' color='#64748b'>{rationale}</font>",
                      S("Normal",fontSize=9,fontName="Helvetica",textColor=DARK,leading=11,spaceAfter=0)),
        ])
    avail=W-2*MARGIN
    t=Table(rows,colWidths=[avail*0.06,avail*0.94])
    t.setStyle(TableStyle([
        ("ROWBACKGROUNDS",(0,0),(-1,-1),[WHITE,GREY_LT]),
        ("LINEABOVE",(0,0),(-1,0),0.8,color),("LINEBEFORE",(0,0),(0,-1),3,color),
        ("GRID",(0,0),(-1,-1),0.3,LINE),("VALIGN",(0,0),(-1,-1),"TOP"),
        ("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5),("LEFTPADDING",(0,0),(-1,-1),8),
    ]))
    return t

def rules_table(rules_list,color):
    if not rules_list:
        return Paragraph("No significant rules found at the specified thresholds.",body_sm)
    headers=["If customer buys","They also buy","Support","Confidence","Lift"]
    data=[[ant,cons,f"{float(sup):.3f}",f"{float(conf):.2%}",f"{float(lift):.2f}"]
          for ant,cons,sup,conf,lift in rules_list]
    avail=W-2*MARGIN
    return styled_table(data,headers,[avail*0.28,avail*0.28,avail*0.13,avail*0.15,avail*0.16],hi_col=4)

# ── Build ─────────────────────────────────────────────────────────────────────
story=[]
doc=SimpleDocTemplate(OUTPUT_PDF, pagesize=A4,
    leftMargin=MARGIN, rightMargin=MARGIN, topMargin=MARGIN, bottomMargin=MARGIN)

# ── Cover Page ────────────────────────────────────────────────────────────────
story.append(Spacer(1, 1.5*cm))
story.append(ColorBar(NAVY, 6))
story.append(Spacer(1, 1.5*cm))

story.append(Paragraph("Customer Segmentation", title_s))
story.append(Paragraph("Executive Report", subtitle_s))

story.append(Spacer(1, 0.5*cm))
story.append(HRFlowable(width="60%", thickness=1, color=LINE, spaceAfter=20, hAlign="CENTER"))

# Student Information
story.append(Paragraph("Machine Learning II  |  Nova IMS  |  Data Science Degree", uni_s))
story.append(Spacer(1, 0.2*cm))
# Replace XXXX with actual numbers
story.append(Paragraph("Leonardo Sousa – 2024XXXX", student_s)) 
story.append(Paragraph("Jaime Abreu – 2024XXXX", student_s))
story.append(Paragraph("Afonso Fonseca – 20241781", student_s))

story.append(Spacer(1, 1.5*cm))
story.append(kv_table([
    ("Total Customers","33,038"),
    ("Segments Identified","5"),
    ("Algorithm","K-Means (k=5, StandardScaler, n_init=15)"),
    ("Basket Rules","Apriori (min support 1%, min confidence 25%, min lift 1.1)"),
    ("Largest Segment","Core Everyday Shoppers — 40.7% of base"),
    ("Highest-Value Segment","High-Value Families — EUR 42,729 avg lifetime spend"),
]))
story.append(Spacer(1, 0.8*cm))
story.append(img("radar_chart.png", width=12*cm))
story.append(PageBreak())

# ── Table of Contents ─────────────────────────────────────────────────────────
story.append(SectionHeader("Table of Contents", NAVY))
story.append(Spacer(1, 0.4*cm))
for num,title in [("1","Executive Summary"),("2","Exploratory Data Analysis and Pre-Processing"),
                   ("3","Customer Segmentation and Clustering"),("4","Targeted Promotion"),
                   ("5","Conclusion and Recommendations")]:
    story.append(Paragraph(f"<b>{num}.</b>  {title}", toc_s))
story.append(Spacer(1, 1.2*cm)) # Replaced PageBreak with Spacer for continuous flow

# ── 1 Executive Summary ───────────────────────────────────────────────────────
story.append(KeepTogether([
    SectionHeader("1   Executive Summary", BLUE),
    Spacer(1, 0.4*cm),
    Paragraph(
        "This report presents the findings of a customer segmentation study on a retail customer base "
        "of 33,038 individuals. Using K-Means clustering applied to demographic, spend-behaviour and "
        "transaction history features, five distinct segments were identified. Each segment is profiled "
        "in terms of size, spending behaviour, demographics and loyalty characteristics. Targeted "
        "marketing campaigns grounded in basket association rules are proposed for each group.", body_s)
]))

story.append(Paragraph("Key Findings", h2_s))
for f in [
    "<b>High-Value Families</b> (21% of customers) generate an estimated 38% of total lifetime revenue. "
    "Their average spend of EUR 42,729 is 2.5x the portfolio average.",
    "<b>Core Everyday Shoppers</b> are the largest segment at 41% of the base and represent the largest "
    "absolute revenue pool.",
    "<b>Budget-Conscious Shoppers</b> visit the most distinct stores, signalling active cross-shopping.",
    "<b>Tech-Savvy Singles</b> and <b>Pet and Home Essentials</b> customers have clearly defined category "
    "affinities addressable through targeted promotions.",
]:
    story.append(bullet(f))
story.append(Spacer(1, 0.3*cm))

story.append(KeepTogether([
    Paragraph("Spend Distribution", h2_s),
    img("dist_total_spend.png", width=W-2*MARGIN),
    Paragraph("Figure 1: Distribution of total lifetime spend.", caption_s)
]))
story.append(Spacer(1, 1.2*cm))

# ── 2 EDA ─────────────────────────────────────────────────────────────────────
story.append(KeepTogether([
    SectionHeader("2   Exploratory Data Analysis and Pre-Processing", C_EDA),
    Spacer(1, 0.4*cm),
    Paragraph("Dataset Overview", h2_s),
    Paragraph(
        "Two datasets were provided: <b>customer_info</b> containing 33,038 customer records with demographic "
        "and lifetime spend information, and <b>customer_basket</b> containing 100,000 randomly sampled shopping "
        "baskets. The datasets are linked via customer_id.", body_s)
]))

story.append(styled_table(
    [["customer_info","33,038","Demographics, 10 lifetime spend categories, store visit history"],
     ["customer_basket","100,000","invoice_id, customer_id, list of goods per transaction"]],
    ["Dataset","Rows","Key Fields"],
    [(W-2*MARGIN)*0.22,(W-2*MARGIN)*0.13,(W-2*MARGIN)*0.65]))

story.append(Spacer(1, 0.4*cm))
story.append(KeepTogether([
    Paragraph("Feature Distributions", h2_s),
    img("dist_age.png", width=12*cm),
    Paragraph("Figure 2: Customer age distribution across the database.", caption_s)
]))

story.append(KeepTogether([
    img("dist_tenure_years.png", width=12*cm),
    Paragraph("Figure 3: Customer tenure distribution (years).", caption_s)
]))
story.append(Spacer(1, 1.2*cm))

# ── 3 Clustering ──────────────────────────────────────────────────────────────
story.append(KeepTogether([
    SectionHeader("3   Customer Segmentation and Clustering", C_CLUS),
    Spacer(1, 0.4*cm),
    Paragraph("Cluster Selection", h2_s),
    img("elbow_plot.png", width=W-2*MARGIN),
    Paragraph("Figure 4: Elbow curve (inertia) and silhouette score across k = 2 to 9. Both metrics support k = 5.", caption_s)
]))

story.append(Paragraph(
    "The elbow curve shows a clear inflection at k = 5 where the rate of inertia reduction diminishes. "
    "k = 5 simultaneously achieves the highest silhouette score (0.187) across all tested values, "
    "confirming that the clusters are both internally compact and well-separated.", body_s))

story.append(KeepTogether([
    Paragraph("Cluster Visualisation", h2_s),
    img("pca_clusters.png", width=W-2*MARGIN),
    Paragraph("Figure 5: PCA 2D projection of all 33,038 customers coloured by assigned segment.", caption_s)
]))

story.append(Paragraph("Segment Summary", h2_s))
avail=W-2*MARGIN
story.append(styled_table(
    [[SEG_NAMES[i]]+list(SEG_STATS[i]) for i in range(5)],
    ["Segment","Customers","Share","Avg Spend","Avg Age","Avg Children","Avg Tenure"],
    [avail*0.24,avail*0.10,avail*0.08,avail*0.13,avail*0.10,avail*0.14,avail*0.11],hi_col=3))
story.append(Spacer(1, 0.4*cm))

story.append(KeepTogether([
    img("spend_heatmap.png", width=W-2*MARGIN),
    Paragraph("Figure 6: Average lifetime spend per category and segment (EUR).", caption_s)
]))

story.append(Paragraph("Segment Profiles", h2_s))
for i in range(5):
    color=SEG_HEX[i]; s=SEG_STATS[i]
    story.append(KeepTogether([
        SegmentBadge(SEG_NAMES[i],color,s[0],s[1],s[2]),
        Spacer(1,0.2*cm),
        Paragraph(SEG_DESC[i],body_s),
        Paragraph("Defining Characteristics",h3_s),
        *[bullet(c) for c in SEG_CHARS[i]],
        Spacer(1,0.4*cm),
    ]))
story.append(Spacer(1, 0.8*cm))

# ── 4 Targeted Promotion ──────────────────────────────────────────────────────
story.append(KeepTogether([
    SectionHeader("4   Targeted Promotion", C_CAMP),
    Spacer(1, 0.4*cm),
    Paragraph(
        "Targeted promotions were designed for each segment using basket association rules mined via the "
        "Apriori algorithm on the customer_basket dataset. Rules were computed separately per cluster "
        "to ensure segment-specific relevance.", body_s)
]))

for i in range(5):
    color=SEG_HEX[i]; s=SEG_STATS[i]
    story.append(Spacer(1,0.2*cm))
    story.append(KeepTogether([
        SegmentBadge(SEG_NAMES[i],color,s[0],s[1],s[2]),
        Spacer(1,0.2*cm),
        Paragraph("Campaign Initiatives",h3_s),
        campaign_block(SEG_CAMPAIGNS[i],color)
    ]))
    if top_rules.get(str(i)):
        story.append(KeepTogether([
            Paragraph("Supporting Association Rules",h3_s),
            rules_table(top_rules[str(i)],color),
            Spacer(1,0.2*cm)
        ]))
story.append(Spacer(1, 0.8*cm))

# ── 5 Conclusion ──────────────────────────────────────────────────────────────
story.append(KeepTogether([
    SectionHeader("5   Conclusion and Recommendations", C_CONC),
    Spacer(1, 0.4*cm),
    Paragraph("Summary", h2_s),
    Paragraph(
        "Five meaningfully distinct customer segments were identified through K-Means clustering, validated "
        "by both elbow and silhouette analysis. The segments are differentiated primarily by category spend "
        "composition, household structure, customer tenure and price sensitivity.", body_s)
]))

story.append(Paragraph("Segment-Level Recommendations", h2_s))
for name,body in [
    ("High-Value Families","Priority retention target. Invest in a VIP loyalty tier with meaningful cashback and milestone rewards."),
    ("Core Everyday Shoppers","Largest revenue pool due to segment size. Cross-category promotions in fresh produce and groceries grow basket size without requiring price discounting."),
    ("Budget-Conscious Shoppers","Loyalty and consolidation are the twin goals. A mid-week loyalty event and household bundle offers reward in-store consolidation."),
    ("Tech-Savvy Singles","Technology product affinity is strong. Launch-aligned campaigns and device trade-in programmes are the highest-fit interventions."),
    ("Pet and Home Essentials","Subscription conversion is the strategic priority. High purchase regularity in pet food and hygiene makes this segment ideally suited for a subscribe-and-save programme."),
]:
    story.append(KeepTogether([
        Paragraph(name, h3_s),
        Paragraph(body, body_s)
    ]))

story.append(Spacer(1, 1.5*cm))
story.append(HRFlowable(width="100%", thickness=1, color=LINE, spaceBefore=6, spaceAfter=12))
story.append(Paragraph("Machine Learning II  |  Nova IMS  |  Data Science",
    S("Normal", fontSize=8, fontName="Helvetica", textColor=GREY, alignment=TA_CENTER)))

doc.build(story)
print(f"PDF built successfully at {OUTPUT_PDF}")
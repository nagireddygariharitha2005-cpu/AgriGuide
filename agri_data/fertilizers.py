"""
Fertilizer database and dosage guidance module for AgriGuide.
Contains authentic nutrient formulations, bilingual terminology, and crop-specific guidance.
"""

from typing import Dict, Any, List, Optional

FERTILIZERS_CATALOG = {
    "urea": {
        "id": "urea",
        "name_en": "Urea (46-0-0)",
        "name_te": "యూరియా (నత్రజని ఎరువు)",
        "formula": "CO(NH₂)₂",
        "npk_content": "46% Nitrogen (N)",
        "primary_nutrient": "Nitrogen / నత్రజని",
        "category": "Chemical Nitrogenous Fertilizer",
        "category_te": "రసాయన నత్రజని ఎరువు",
        "description_en": "White crystalline solid delivering the highest concentration of nitrogen. Essential for vegetative growth, leafy expansion, chlorophyll synthesis, and vigorous tillering.",
        "description_te": "తెల్లటి గుళికల రూపంలో ఉండే అధిక నత్రజని ఎరువు. మొక్క శాఖీయ ఎదుగుదల, పచ్చదనం, పిలకలు రావడానికి మరియు కిరణజన్య సంయోగక్రియకు అత్యంత ముఖ్యం.",
        "application_tips_en": "Never broadcast on dry soil under intense sunlight (leads to ammonia volatilization loss). Apply in standing moist soil and incorporate immediately. Split into 2-3 stages.",
        "application_tips_te": "ఎండిన నేలపై లేదా మధ్యాహ్నం ఎండలో చల్లకూడదు (నత్రజని ఆవిరైపోతుంది). నేలలో తగినంత తేమ ఉన్నప్పుడు వేసి మట్టిలో కలిసేలా చేయాలి.",
        "safety_warning_en": "Excessive urea application causes soft succulent foliage, inviting severe attacks of sucking pests, lodging of crops, and delayed maturity.",
        "safety_warning_te": "యూరియా మోతాదుకు మించి వాడితే మొక్కలు గుబురుగా పెరిగి రసం పీల్చే పురుగులు, తెగుళ్లు అధికంగా ఆశిస్తాయి."
    },
    "dap": {
        "id": "dap",
        "name_en": "DAP - Di-Ammonium Phosphate (18-46-0)",
        "name_te": "డీఏపీ - డై అమ్మోనియం ఫాస్ఫేట్ (భాస్వరం ఎరువు)",
        "formula": "(NH₄)₂HPO₄",
        "npk_content": "18% Nitrogen (N) + 46% Phosphorus (P₂O₅)",
        "primary_nutrient": "Phosphorus & Starter Nitrogen / భాస్వరం మరియు నత్రజని",
        "category": "Complex Phosphate Fertilizer",
        "category_te": "మిశ్రమ భాస్వరం ఎరువు",
        "description_en": "Premier basal fertilizer supplying readily available water-soluble phosphate along with starter nitrogen. Vital for early seedling root development, sturdy stalk formation, and flower initiation.",
        "description_te": "విత్తే సమయంలో లేదా నాటే సమయంలో వేసే ప్రధాన ఎరువు. మొక్క వేర్లు లోతుగా నాటుకోవడానికి, కొమ్మలు బలంగా ఎదగడానికి మరియు పూతకు దోహదపడుతుంది.",
        "application_tips_en": "Apply as basal placement near the root zone during sowing or transplanting. Do not mix directly with calcium or zinc sulphate as it causes fixation.",
        "application_tips_te": "విత్తే సమయంలో విత్తనాలకు దగ్గరగా లోతుగా వేయాలి. జింక్ సల్ఫేట్‌తో కలిపి నేరుగా వాడకూడదు.",
        "safety_warning_en": "Phosphate does not move freely in soil; surface broadcasting without soil incorporation results in poor root uptake.",
        "safety_warning_te": "భాస్వరం నేల పైపొరల్లో స్థిరపడుతుంది కాబట్టి విత్తనం పడే లోతులో వేయాలి."
    },
    "mop": {
        "id": "mop",
        "name_en": "MOP - Muriate of Potash (0-0-60)",
        "name_te": "పొటాష్ - మ్యూరియేట్ ఆఫ్ పొటాష్",
        "formula": "KCl (Potassium Chloride)",
        "npk_content": "60% Potash (K₂O)",
        "primary_nutrient": "Potassium / పొటాషియం",
        "category": "Potassic Fertilizer",
        "category_te": "పొటాష్ ఎరువు",
        "description_en": "Essential for disease and drought resistance, enzyme activation, stomatal regulation, grain filling, luster, and keeping quality of produce.",
        "description_te": "పంటలకు రోగనిరోధక శక్తిని, కరువును తట్టుకునే శక్తిని ఇస్తుంది. గింజలు బరువుగా, నాణ్యంగా మారడానికి పొటాష్ అత్యవసరం.",
        "application_tips_en": "Apply 50% basal and 50% at reproductive (panicle/boll/pod) filling stage. In sandy soils, split into 3 doses.",
        "application_tips_te": "సగం ఆఖరి దుక్కిలో, మిగతా సగం పూత మరియు కాయ ఊరే దశలో వేయాలి.",
        "safety_warning_en": "Avoid in chloride-sensitive crops like tobacco and certain berries; use Potassium Sulphate (SOP) instead.",
        "safety_warning_te": "పొగాకు లాంటి క్లోరైడ్ సున్నిత పంటలలో దీని బదులు ఎస్‌ఓపీ (SOP) వాడాలి."
    },
    "npk_20_20_0_13": {
        "id": "npk_20_20_0_13",
        "name_en": "Complex 20:20:0:13 (Ammonium Phosphate Sulphate)",
        "name_te": "20:20:0:13 కాంప్లెక్స్ ఎరువు",
        "formula": "N-P-K-S Complex",
        "npk_content": "20% N + 20% P₂O₅ + 0% K + 13% Sulphur (S)",
        "primary_nutrient": "Nitrogen, Phosphorus, and Sulphur / నత్రజని, భాస్వరం, గంధకం",
        "category": "Multi-Nutrient Complex",
        "category_te": "బహుళ పోషక కాంప్లెక్స్",
        "description_en": "Specially formulated for oilseeds (groundnut, mustard, sunflower) and pulses. The 13% water-soluble sulphur increases oil content and protein formation significantly.",
        "description_te": "నూనెగింజలు (వేరుశనగ, పొద్దుతిరుగుడు) మరియు పప్పుదినుసులకు అత్యుత్తమమైనది. ఇందులో ఉండే 13% సల్ఫర్ (గంధకం) నూనె శాతాన్ని పెంచుతుంది.",
        "application_tips_en": "Best applied at basal or early vegetative stage for rapid root nodule development and foliage growth.",
        "application_tips_te": "విత్తే సమయంలో లేదా తొలి దశలో దుక్కిలో వేస్తే వేర్ల గ్రంథులు బలంగా అభివృద్ధి చెందుతాయి.",
        "safety_warning_en": "Complement with potash (MOP) if soil test indicates low available potassium.",
        "safety_warning_te": "నేలలో పొటాష్ లోపం ఉంటే విడిగా పొటాష్ ఎరువును తప్పనిసరిగా వేసుకోవాలి."
    },
    "ssp": {
        "id": "ssp",
        "name_en": "SSP - Single Super Phosphate (0-16-0-11)",
        "name_te": "సింగిల్ సూపర్ ఫాస్ఫేట్ (ఎస్ఎస్పీ)",
        "formula": "Ca(H₂PO₄)₂ + CaSO₄",
        "npk_content": "16% P₂O₅ + 19% Calcium + 11% Sulphur",
        "primary_nutrient": "Phosphorus, Calcium & Sulphur",
        "category": "Phosphate & Secondary Nutrients",
        "category_te": "భాస్వరం మరియు క్యాల్షియం ఎరువు",
        "description_en": "Provides economical phosphorus accompanied by significant calcium (19%) and sulphur (11%). Ideal for groundnut and pulses in neutral to alkaline soils.",
        "description_te": "తక్కువ ఖర్చుతో భాస్వరంతో పాటు క్యాల్షియం, సల్ఫర్ అందించే ఎరువు. వేరుశనగ పంటకు ఎంతో ప్రయోజనకరం.",
        "application_tips_en": "Incorporate during final land preparation in root zone.",
        "application_tips_te": "ఆఖరి దుక్కిలో వేసి భూమిలో కలియదున్నాలి.",
        "safety_warning_en": "Store in dry place; absorbs atmospheric moisture quickly.",
        "safety_warning_te": "తేమ లేని పొడి ప్రదేశంలో నిల్వ ఉంచాలి."
    },
    "zinc_sulphate": {
        "id": "zinc_sulphate",
        "name_en": "Zinc Sulphate (ZnSO₄ 21% or 33%)",
        "name_te": "జింక్ సల్ఫేట్ (సూక్ష్మ పోషక ఎరువు)",
        "formula": "ZnSO₄·7H₂O",
        "npk_content": "21% or 33% Zinc (Zn) + Sulphur",
        "primary_nutrient": "Micronutrient Zinc / జింక్ సూక్ష్మపోషకం",
        "category": "Micronutrient Fertilizer",
        "category_te": "సూక్ష్మ పోషక ఎరువు",
        "description_en": "Crucial micronutrient preventing Khaira disease in paddy and white bud in maize. Enhances auxin hormone synthesis and leaf size.",
        "description_te": "వరిలో ఖైరా తెగులు, ఆకుల్లో తుప్పు మచ్చలు మరియు మొక్కజొన్నలో తెల్ల మొగ్గ రాకుండా కాపాడుతుంది.",
        "application_tips_en": "Soil application @ 20 kg/acre (21%) or foliar spray @ 2g/L water mixed with 10g urea. Do NOT mix with DAP/SSP.",
        "application_tips_te": "ఎకరానికి 20 కిలోలు ఆఖరి దుక్కిలో వేయాలి. లేదా లీటరు నీటికి 2 గ్రాముల జింక్ + 10 గ్రాముల యూరియా కలిపి పిచికారీ చేయాలి. డీఏపీతో కలపరాదు.",
        "safety_warning_en": "Never combine directly with phosphatic fertilizers (DAP/SSP) in the same spray tank or application bucket (precipitates into insoluble zinc phosphate).",
        "safety_warning_te": "డీఏపీ లేదా సూపర్ ఫాస్ఫేట్ తో కలిపి వాడకూడదు."
    },
    "vermicompost": {
        "id": "vermicompost",
        "name_en": "Organic Vermicompost / FYM",
        "name_te": "సేంద్రీయ వర్మీకంపోస్ట్ / పశువుల ఎరువు",
        "formula": "Bio-organic Matrix",
        "npk_content": "1.5 - 2.5% N, 1.0 - 1.5% P, 1.5% K + Micronutrients & Microbes",
        "primary_nutrient": "Soil Organic Carbon & Humus / సేంద్రీయ కర్బనం",
        "category": "Organic Bio-Fertilizer",
        "category_te": "సేంద్రీయ జీవ ఎరువు",
        "description_en": "Earthworm-processed compost rich in beneficial soil bacteria, mycorrhizae, and humic acid. Enhances water-holding capacity, soil aeration, and nutrient use efficiency.",
        "description_te": "వానపాముల ఎరువు నేల భౌతిక స్థితిని మెరుగుపరుస్తుంది. నేలలో ఉపయోగకరమైన బ్యాక్టీరియాను పెంచి రసాయన ఎరువుల సామర్థ్యాన్ని పెంచుతుంది.",
        "application_tips_en": "Apply 1-2 tonnes/acre during land preparation. Can be combined with bio-fertilizers (Rhizobium, Azospirillum, PSB).",
        "application_tips_te": "ఎకరానికి 1-2 టన్నులు ఆఖరి దుక్కిలో చల్లి కలియదున్నాలి.",
        "safety_warning_en": "Ensure compost is well-cured and odor-free; immature dung can introduce weed seeds and root grubs.",
        "safety_warning_te": "మంచిగా మాగిన ఎరువును మాత్రమే వాడాలి; పచ్చి పేడ వాడితే చెదలు, పురుగులు వచ్చే ప్రమాదం ఉంది."
    }
}


def calculate_fertilizer_guidance(crop: str, acres: float = 1.0) -> Dict[str, Any]:
    """
    Computes indicative fertilizer guidance for Indian agro-climatic conditions.
    Explicitly includes caveats regarding soil tests, regional recommendations,
    and safe split-dose applications.
    """
    crop_key = crop.lower().strip()
    acres = max(0.25, min(float(acres), 100.0))

    # Standard per-acre recommendations (in 50-kg bags)
    recommendations_db = {
        "rice": {
            "urea_bags": round(1.8 * acres, 1),
            "dap_bags": round(1.0 * acres, 1),
            "mop_bags": round(0.7 * acres, 1),
            "zinc_kg": round(20 * acres, 1),
            "schedule_en": "Basal: Full DAP + 1/3 MOP; 30 Days: 1/3 Urea; 60 Days: 1/3 Urea + 1/3 MOP; Flowering: Remaining Urea.",
            "schedule_te": "నాట్లు వేసేటప్పుడు: మొత్తం డీఏపీ + 1/3 పొటాష్; 30 రోజులకు: 1/3 యూరియా; 60 రోజులకు: 1/3 యూరియా + 1/3 పొటాష్; పూత దశలో: మిగిలిన యూరియా."
        },
        "cotton": {
            "urea_bags": round(2.2 * acres, 1),
            "dap_bags": round(1.2 * acres, 1),
            "mop_bags": round(0.9 * acres, 1),
            "zinc_kg": round(15 * acres, 1),
            "schedule_en": "Basal: Full DAP; 30 Days: 1/3 Urea; 60 Days: 1/3 Urea + 1/2 MOP; 90 Days: 1/3 Urea + 1/2 MOP.",
            "schedule_te": "విత్తేటప్పుడు: మొత్తం డీఏపీ; 30 రోజులకు: 1/3 యూరియా; 60 రోజులకు: 1/3 యూరియా + సగం పొటాష్; 90 రోజులకు: 1/3 యూరియా + మిగతా పొటాష్."
        },
        "maize": {
            "urea_bags": round(2.0 * acres, 1),
            "dap_bags": round(1.0 * acres, 1),
            "mop_bags": round(0.6 * acres, 1),
            "zinc_kg": round(15 * acres, 1),
            "schedule_en": "Basal: Full DAP + 1/3 Urea + Full MOP; Knee-high (30 days): 1/3 Urea; Tasseling (55 days): 1/3 Urea.",
            "schedule_te": "విత్తేటప్పుడు: మొత్తం డీఏపీ + 1/3 యూరియా + మొత్తం పొటాష్; మోకాలు ఎత్తు (30 రోజులకు): 1/3 యూరియా; పూత (కంకి) దశలో: 1/3 యూరియా."
        },
        "groundnut": {
            "urea_bags": round(0.5 * acres, 1),
            "dap_bags": round(0.8 * acres, 1),
            "mop_bags": round(0.6 * acres, 1),
            "gypsum_kg": round(200 * acres, 1),
            "schedule_en": "Basal: All Urea, DAP, and MOP; 40-45 Days (Pegging): Apply 200 kg Gypsum/acre and incorporate lightly.",
            "schedule_te": "విత్తేటప్పుడు: యూరియా, డీఏపీ, పొటాష్ కలిపి వేయాలి; 40-45 రోజులకు: ఎకరానికి 200 కిలోల జిప్సం తప్పనిసరిగా వేసి మట్టి ఎగదోయాలి."
        },
        "chilli": {
            "urea_bags": round(2.5 * acres, 1),
            "dap_bags": round(1.5 * acres, 1),
            "mop_bags": round(1.2 * acres, 1),
            "zinc_kg": round(15 * acres, 1),
            "schedule_en": "Split nitrogen into 4 doses across vegetative, flowering, and picking flushes. Apply Calcium Nitrate during fruiting.",
            "schedule_te": "నత్రజని ఎరువును 4 దఫాలుగా వేయాలి. పూత మరియు కాయ దశలలో క్యాల్షియం నైట్రేట్, బోరాన్ పిచికారీ చేయడం ప్రయోజనకరం."
        }
    }

    selected = recommendations_db.get(crop_key, recommendations_db["rice"])

    return {
        "crop": crop,
        "acres": acres,
        "urea_bags": selected.get("urea_bags", round(1.5 * acres, 1)),
        "dap_bags": selected.get("dap_bags", round(1.0 * acres, 1)),
        "mop_bags": selected.get("mop_bags", round(0.6 * acres, 1)),
        "zinc_or_gypsum": selected.get("gypsum_kg") or selected.get("zinc_kg", round(15 * acres, 1)),
        "zinc_or_gypsum_unit": "kg Gypsum" if "gypsum_kg" in selected else "kg Zinc Sulphate",
        "schedule_en": selected.get("schedule_en"),
        "schedule_te": selected.get("schedule_te"),
        "disclaimer_en": "IMPORTANT: These are indicative guidelines. Actual dosage depends on soil test reports (Soil Health Card), seed variety, and regional agricultural university recommendations.",
        "disclaimer_te": "గమనిక: ఇవి సాధారణ సూచనలు మాత్రమే. ఖచ్చితమైన ఎరువుల మోతాదు భూసార పరీక్ష ఫలితాలు (సాయిల్ హెల్త్ కార్డ్) మరియు స్థానిక వ్యవసాయ విస్తరణాధికారి సలహాపై ఆధారపడి ఉంటుంది."
    }

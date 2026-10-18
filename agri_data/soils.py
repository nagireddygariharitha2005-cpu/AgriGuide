"""
Soil characteristics and agronomic guidance database.
"""

SOIL_PROFILES = {
    "black": {
        "id": "black",
        "name_en": "Black Soil (Regur / Black Cotton Soil)",
        "name_te": "నల్లరేగడి నేల (రేగడి భూమి)",
        "ph_range": "7.2 - 8.5 (Slightly Alkaline)",
        "water_retention": "High (అధిక తేమ నిల్వ సామర్థ్యం)",
        "characteristics_en": "Clayey, rich in calcium carbonate, magnesium, potash and lime. Deep cracks form in summer, promoting aeration. Poor drainage if waterlogged.",
        "characteristics_te": "బంకమట్టి శాతం ఎక్కువ. సున్నం, మెగ్నీషియం, పొటాష్ సమృద్ధిగా ఉంటాయి. ఎండాకాలంలో లోతైన పగుళ్లు ఏర్పడి నేలలో గాలి ప్రసరణ బాగుంటుంది.",
        "best_suited_crops": ["cotton", "rice", "maize", "chilli", "bengalgram", "soybean", "redgram"]
    },
    "red": {
        "id": "red",
        "name_en": "Red Soil (Chalka / Red Sandy Loam)",
        "name_te": "ఎర్ర నేల (చల్కా భూమి / ఎర్రమట్టి)",
        "ph_range": "6.0 - 7.5 (Neutral to slightly acidic)",
        "water_retention": "Low to Moderate (తక్కువ నుండి మధ్యస్థ తేమ నిల్వ)",
        "characteristics_en": "Porous, well-drained, rich in iron and potash, but deficient in nitrogen, phosphorus and humus. Responds excellently to organic manure and regular light irrigation.",
        "characteristics_te": "తేలికపాటి నేల, నీరు త్వరగా ఇంకిపోతుంది. ఇనుము, పొటాష్ ఎక్కువ కానీ నత్రజని, భాస్వరం తక్కువ. పశువుల ఎరువు వేస్తే పంటలు బాగా పండుతాయి.",
        "best_suited_crops": ["groundnut", "cotton", "maize", "redgram", "greengram", "chilli", "millets"]
    },
    "alluvial": {
        "id": "alluvial",
        "name_en": "Alluvial Soil (River Basin / Delta Soil)",
        "name_te": "ఒండ్రు నేల (డెల్టా మరియు నదీ తీర భూమి)",
        "ph_range": "6.5 - 7.5 (Ideal Neutral)",
        "water_retention": "High to Optimal (ఉత్తమ తేమ నిల్వ)",
        "characteristics_en": "Extremely fertile, deposited by rivers, balanced ratio of silt, sand and clay. Rich in potash and phosphoric acid.",
        "characteristics_te": "నదులు మేట వేసిన సారవంతమైన మట్టి. పొటాష్, భాస్వరం అధికం. వరి, గోధుమ, చెరకు, కూరగాయల సాగుకు అత్యుత్తమమైనది.",
        "best_suited_crops": ["rice", "wheat", "maize", "sugarcane", "tomato", "chilli", "greengram"]
    },
    "sandy": {
        "id": "sandy",
        "name_en": "Sandy Soil (Light Soils)",
        "name_te": "ఇసుక నేల (తేలికపాటి ఇసుక భూములు)",
        "ph_range": "5.5 - 7.0",
        "water_retention": "Very Low (త్వరగా ఎండిపోయే నేల)",
        "characteristics_en": "Fast draining, low nutrient-holding capacity, warms up quickly. Requires frequent irrigation, split fertilizer application, and mulching.",
        "characteristics_te": "నీటిని నిల్వ ఉంచలేదు, పోషకాలు త్వరగా కొట్టుకుపోతాయి. తక్కువ వ్యవధిలో తడులు ఇవ్వాలి. సేంద్రీయ ఎరువులు, మల్చింగ్ అవసరం.",
        "best_suited_crops": ["groundnut", "watermelon", "millets", "cowpea", "greengram"]
    },
    "clay": {
        "id": "clay",
        "name_en": "Clayey Heavy Soil",
        "name_te": "బంకమట్టి నేల (బరువైన నేలలు)",
        "ph_range": "7.0 - 8.2",
        "water_retention": "Very High (అత్యధిక తేమ నిల్వ, నీటి నిల్వ సమస్యలు రావచ్చు)",
        "characteristics_en": "Fine particle texture, compacts easily. Excellent for wetland paddy cultivation, but needs careful drainage for dry crops.",
        "characteristics_te": "నేల కణాలు చాలా చిన్నవి, నీటిని ఎక్కువగా పట్టి ఉంచుతుంది. వరి సాగుకు అనుకూలం. ఆరుతడి పంటలకు మురుగునీటి వసతి తప్పనిసరి.",
        "best_suited_crops": ["rice", "cotton", "wheat", "soybean"]
    },
    "loamy": {
        "id": "loamy",
        "name_en": "Loamy Soil (Balanced Agricultural Soil)",
        "name_te": "గరప నేల (సమతుల్య వ్యవసాయ భూమి)",
        "ph_range": "6.0 - 7.5",
        "water_retention": "Optimal (ఆదర్శవంతమైన తేమ మరియు గాలి ప్రసరణ)",
        "characteristics_en": "The gold standard for farming. Contains an ideal mixture of sand, silt, and clay with high humus and aeration.",
        "characteristics_te": "వ్యవసాయానికి అత్యుత్తమ నేల. ఇసుక, ఒండ్రు, బంకమట్టి సమాన నిష్పత్తిలో ఉండి పోషకాలు అధికంగా ఉంటాయి.",
        "best_suited_crops": ["maize", "cotton", "tomato", "chilli", "wheat", "groundnut", "redgram"]
    }
}

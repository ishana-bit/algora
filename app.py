
# ================================================================
# ALGORA v3 | STREAMLIT WEBSITE
# Model-guided microalgae growth and energy optimiser
# ================================================================

import streamlit as st
import numpy as np
import plotly.graph_objects as go


# ================================================================
# 1. PAGE CONFIGURATION
# ================================================================

st.set_page_config(
    page_title="ALGORA | Microalgae Optimiser",
    page_icon="🌲",
    layout="wide"
)


# ================================================================
# 2. CUSTOM WEBSITE DESIGN
# ================================================================

st.markdown("""
<style>

.stApp {
    background-color: #f5f7ef;
}

[data-testid="stHeader"] {
    background-color: transparent;
}

.main .block-container {
    max-width: 1150px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

.hero {
    background: linear-gradient(
        120deg,
        #102b26,
        #174c3c,
        #28634d
    );
    padding: 35px;
    border-radius: 18px;
    color: #f4f5e9;
    margin-bottom: 28px;
}

.hero-small {
    font-size: 12px;
    letter-spacing: 4px;
    color: #b9d8bd;
}

.hero-title {
    font-size: 48px;
    font-weight: 800;
    letter-spacing: 5px;
    margin-top: 8px;
}

.hero-subtitle {
    font-size: 15px;
    color: #d2e4d2;
    margin-top: 8px;
}

.section-title {
    color: #28563d;
    font-size: 23px;
    font-weight: 700;
    margin-top: 22px;
    margin-bottom: 12px;
}

.result-card {
    background: #edf4ed;
    border-left: 5px solid #43865e;
    padding: 20px;
    border-radius: 11px;
    margin-bottom: 15px;
    color: #20392b;
}

.result-heading {
    font-size: 12px;
    letter-spacing: 1.5px;
    color: #568267;
    font-weight: bold;
}

.result-description {
    font-size: 13px;
    color: #45604d;
    margin-top: 8px;
    margin-bottom: 12px;
}

.result-value {
    font-size: 14px;
    line-height: 1.9;
}

.info-card {
    background: #eaf1e9;
    padding: 18px;
    border-radius: 11px;
    color: #48604c;
    font-size: 13px;
    line-height: 1.8;
}

div.stButton > button {
    background-color: #28634d;
    color: white;
    border: none;
    border-radius: 9px;
    min-height: 43px;
    font-weight: 600;
}

div.stButton > button:hover {
    background-color: #174c3c;
    color: white;
    border: none;
}

/* ALGORA SLIDER COLOURS */

div[data-testid="stSlider"] [role="slider"] {
    background-color: #55A6D9 !important;
    border: 2px solid #FFFFFF !important;
}

div[data-testid="stSlider"] [data-baseweb="slider"] > div > div {
    background-color: #55A6D9 !important;
}

div[data-testid="stSlider"] div[role="slider"] {
    box-shadow: 0 0 0 3px rgba(85, 166, 217, 0.2) !important;
}

</style>
""", unsafe_allow_html=True)


# ================================================================
# 3. LITERATURE-BASED MODEL PARAMETERS
# ================================================================

MU_MAX = 0.553
LIGHT_HALF_SATURATION = 275.116

TEMP_OPTIMUM = 26.0
TEMP_WIDTH = 3.3
REFERENCE_TEMPERATURE = 30.0

REFERENCE_PHOTOPERIOD = 12.0

INITIAL_BIOMASS = 0.05
CARRYING_CAPACITY = 1.0


# ================================================================
# 4. BIOLOGICAL RESPONSE FUNCTIONS
# ================================================================

def light_growth_rate(ppfd):

    return (
        MU_MAX * ppfd
        / (LIGHT_HALF_SATURATION + ppfd)
    )


def temperature_factor(temp):

    numerator = np.exp(
        -((temp - TEMP_OPTIMUM) ** 2)
        / (2 * TEMP_WIDTH ** 2)
    )

    reference = np.exp(
        -((REFERENCE_TEMPERATURE - TEMP_OPTIMUM) ** 2)
        / (2 * TEMP_WIDTH ** 2)
    )

    return numerator / reference


def photoperiod_factor(hours):

    return hours / REFERENCE_PHOTOPERIOD


# ================================================================
# 5. PREDICTED MICROALGAE GROWTH
# ================================================================

def predict_growth(ppfd, hours, temp, days):

    light_mu = light_growth_rate(ppfd)

    temp_multiplier = temperature_factor(temp)

    photoperiod_multiplier = photoperiod_factor(hours)

    # LED electrical power is NOT included in biological growth.

    effective_mu = (
        light_mu
        * temp_multiplier
        * photoperiod_multiplier
    )

    time = np.linspace(0, days, 150)

    A = (
        CARRYING_CAPACITY - INITIAL_BIOMASS
    ) / INITIAL_BIOMASS

    biomass = CARRYING_CAPACITY / (
        1 + A * np.exp(-effective_mu * time)
    )

    return time, biomass, effective_mu


# ================================================================
# 6. ELECTRICITY AND ENERGY EFFICIENCY
# ================================================================

def calculate_energy(led_power, hours, days):

    energy = (
        led_power * hours * days
    ) / 1000

    return energy


# ================================================================
# 7. COMBINED PREDICTION METRICS
# ================================================================

def calculate_metrics(
    ppfd,
    hours,
    temp,
    days,
    led_power
):

    time, biomass, mu = predict_growth(
        ppfd,
        hours,
        temp,
        days
    )

    final_biomass = biomass[-1]

    energy = calculate_energy(
        led_power,
        hours,
        days
    )

    biomass_increase = (
        final_biomass - INITIAL_BIOMASS
    )

    efficiency = (
        biomass_increase / max(energy, 1e-12)
    )

    return {
        "time": time,
        "biomass_curve": biomass,
        "growth_rate": mu,
        "final_biomass": final_biomass,
        "biomass_increase": biomass_increase,
        "energy": energy,
        "efficiency": efficiency
    }


# ================================================================
# 8. AUTOMATIC OPTIMISATION
# ================================================================

def optimise_conditions(days, power):

    best_growth = None
    best_efficiency = None

    ppfd_values = np.arange(130, 521, 10)
    hours_values = np.arange(6, 19, 1)

    temperature_values = np.arange(
        24.5, 28.6, 0.5
    )

    for ppfd in ppfd_values:

        for hours in hours_values:

            for temp in temperature_values:

                result = calculate_metrics(
                    ppfd,
                    hours,
                    temp,
                    days,
                    power
                )

                candidate = {
                    "ppfd": ppfd,
                    "hours": hours,
                    "temp": temp,
                    "biomass": result["final_biomass"],
                    "growth_rate": result["growth_rate"],
                    "energy": result["energy"],
                    "efficiency": result["efficiency"]
                }

                # Objective A: maximum final biomass

                if (
                    best_growth is None
                    or candidate["biomass"]
                    > best_growth["biomass"]
                ):

                    best_growth = candidate

                # Objective B: maximum biomass per kWh

                if (
                    best_efficiency is None
                    or candidate["efficiency"]
                    > best_efficiency["efficiency"]
                ):

                    best_efficiency = candidate

    return best_growth, best_efficiency


# ================================================================
# 9. RESULT CARD
# ================================================================

def result_card(title, result, description):

    return f"""
    <div class="result-card">

        <div class="result-heading">
            {title}
        </div>

        <div class="result-description">
            {description}
        </div>

        <div class="result-value">

            <b>Light intensity:</b>
            {result['ppfd']} PPFD<br>

            <b>Light duration:</b>
            {result['hours']} hours/day<br>

            <b>Temperature:</b>
            {result['temp']} °C<br>

            <b>Predicted biomass:</b>
            {result['biomass']:.4f}<br>

            <b>Growth rate:</b>
            {result['growth_rate']:.4f} day⁻¹<br>

            <b>Electricity:</b>
            {result['energy']:.4f} kWh<br>

            <b>Energy efficiency:</b>
            {result['efficiency']:.4f} relative units/kWh

        </div>

    </div>
    """


# ================================================================
# 10. WEBSITE HEADER
# ================================================================

st.markdown("""
<div style="
    background: linear-gradient(120deg, #123D32, #246B55);
    padding: 38px 35px;
    border-radius: 18px;
    margin-bottom: 25px;
    text-align: left;
">
    <div style="
        color: #B9D8C7;
        font-size: 13px;
        letter-spacing: 5px;
        font-weight: 600;
        margin-bottom: 18px;
    ">
        MODEL-GUIDED MICROALGAE CULTIVATION
    </div>

    <div style="
        color: #FFFFFF;
        font-size: 58px;
        font-weight: 800;
        letter-spacing: 3px;
        line-height: 1.2;
    ">
        ALGORA
    </div>

    <div style="
        color: #D6E9DF;
        font-size: 20px;
        margin-top: 8px;
    ">
        Predict. Optimise. Validate.
    </div>

    <div style="
        color: #B9D8C7;
        font-size: 11px;
        letter-spacing: 2px;
        margin-top: 25px;
    ">
        MATHEMATICAL MODELLING &nbsp; • &nbsp; SUSTAINABILITY &nbsp; • &nbsp; MICROALGAE
    </div>
</div>
""", unsafe_allow_html=True)

# ================================================================
# 11. ENVIRONMENTAL INPUTS
# ================================================================

st.markdown(
    '<div class="section-title">ENVIRONMENTAL CONTROL PANEL</div>',
    unsafe_allow_html=True
)

col1, col2 = st.columns(2)

with col1:

    ppfd = st.slider(
        "Light intensity (PPFD)",
        min_value=130,
        max_value=520,
        value=260,
        step=10,
        help="Photosynthetic photon flux density at the culture."
    )

    hours = st.slider(
        "Daily light duration (hours)",
        min_value=6,
        max_value=18,
        value=12,
        step=1
    )

with col2:

    temp = st.slider(
        "Temperature (°C)",
        min_value=24.5,
        max_value=28.5,
        value=26.0,
        step=0.5
    )

    days = st.slider(
        "Cultivation duration (days)",
        min_value=1,
        max_value=14,
        value=7,
        step=1
    )


power = st.number_input(
    "LED electrical power (W)",
    min_value=0.1,
    max_value=1000.0,
    value=5.0,
    step=0.5,
    help=(
        "Enter the actual electrical power drawn by the LED "
        "at the selected lighting setting."
    )
)

st.caption(
    "LED power is used only to calculate electricity consumption. "
    "It does not directly determine biological growth."
)


# ================================================================
# 12. PREDICTION
# ================================================================

st.divider()

st.markdown(
    '<div class="section-title">MODEL PREDICTION</div>',
    unsafe_allow_html=True
)

if st.button(
    "PREDICT GROWTH",
    use_container_width=True
):

    result = calculate_metrics(
        ppfd,
        hours,
        temp,
        days,
        power
    )

    st.success("Prediction generated.")

    metric1, metric2, metric3 = st.columns(3)

    metric1.metric(
        "Final relative biomass",
        f"{result['final_biomass']:.4f}"
    )

    metric2.metric(
        "Electricity consumed",
        f"{result['energy']:.4f} kWh"
    )

    metric3.metric(
        "Energy efficiency",
        f"{result['efficiency']:.4f}"
    )

    st.write(
        f"**Specific growth rate:** "
        f"{result['growth_rate']:.4f} day⁻¹"
    )

    st.write(
        f"**Predicted biomass increase:** "
        f"{result['biomass_increase']:.4f}"
    )

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=result["time"],
        y=result["biomass_curve"],
        mode="lines",
        name="Predicted biomass",
        line=dict(color="#43865e", width=4),
        fill="tozeroy",
        fillcolor="rgba(67,134,94,0.12)"
    ))

    fig.update_layout(
        title="Predicted Microalgal Growth",
        xaxis_title="Cultivation time (days)",
        yaxis_title="Relative biomass",
        template="plotly_white",
        height=420,
        margin=dict(l=35, r=25, t=60, b=40)
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# ================================================================
# 13. AUTOMATIC OPTIMISATION
# ================================================================

st.divider()

st.markdown(
    '<div class="section-title">AUTOMATIC OPTIMISATION</div>',
    unsafe_allow_html=True
)

st.write(
    "Find the environmental conditions that maximise "
    "biomass production or energy efficiency."
)

if st.button(
    "FIND BOTH OPTIMA",
    use_container_width=True
):

    with st.spinner(
        "Searching possible environmental combinations..."
    ):

        growth, efficiency = optimise_conditions(
            days,
            power
        )

    st.success("Optimisation complete.")

    left, right = st.columns(2)

    with left:

        st.markdown(
            result_card(
                "OPTIMUM A | MAXIMUM BIOMASS",
                growth,
                "Conditions predicted to produce the greatest final biomass."
            ),
            unsafe_allow_html=True
        )

    with right:

        st.markdown(
            result_card(
                "OPTIMUM B | MAXIMUM ENERGY EFFICIENCY",
                efficiency,
                "Conditions predicted to produce the most biomass per kWh."
            ),
            unsafe_allow_html=True
        )

    st.caption(
        "These are model predictions within the selected search ranges, "
        "not experimentally verified optima."
    )


# ================================================================
# 14. EXPERIMENTAL VALIDATION
# ================================================================

st.divider()

st.markdown(
    '<div class="section-title">EXPERIMENTAL VALIDATION</div>',
    unsafe_allow_html=True
)

st.write(
    "Compare the model's predicted growth with actual "
    "optical-density (OD) measurements from a cultivation experiment."
)

st.caption(
    "Enter readings in chronological order, beginning with Day 0. "
    "Example: 0.10, 0.13, 0.17, 0.21, 0.28"
)

observed_text = st.text_input(
    "Measured OD readings",
    placeholder="0.10, 0.13, 0.17, 0.21, 0.28"
)

if st.button(
    "COMPARE MODEL WITH EXPERIMENT",
    use_container_width=True
):

    try:

        observed = np.array([
            float(x.strip())
            for x in observed_text.split(",")
            if x.strip()
        ])

        if len(observed) < 2:

            st.error(
                "Please enter at least two measurements."
            )

        elif np.any(observed <= 0):

            st.error(
                "OD readings must be positive."
            )

        elif len(observed) > days + 1:

            st.error(
                "You have entered more readings than the "
                "selected cultivation duration allows."
            )

        else:

            result = calculate_metrics(
                ppfd,
                hours,
                temp,
                days,
                power
            )

            # Normalise observations to Day 0.
            # This compares relative trends, not absolute biomass.

            observed_relative = observed / observed[0]

            observed_days = np.arange(len(observed))

            predicted_relative = np.interp(
                observed_days,
                result["time"],
                result["biomass_curve"] / INITIAL_BIOMASS
            )

            rmse = np.sqrt(
                np.mean(
                    (
                        observed_relative
                        - predicted_relative
                    ) ** 2
                )
            )

            fig = go.Figure()

            fig.add_trace(go.Scatter(
                x=result["time"],
                y=(
                    result["biomass_curve"]
                    / INITIAL_BIOMASS
                ),
                mode="lines",
                name="Model prediction",
                line=dict(color="#43865e", width=3)
            ))

            fig.add_trace(go.Scatter(
                x=observed_days,
                y=observed_relative,
                mode="markers+lines",
                name="Experimental OD",
                marker=dict(color="#d58a43", size=9),
                line=dict(color="#d58a43", dash="dot")
            ))

            fig.update_layout(
                title="Predicted vs Observed Growth",
                xaxis_title="Cultivation day",
                yaxis_title="Relative value (Day 0 = 1)",
                template="plotly_white",
                height=420
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

            st.metric(
                "Root mean square error (RMSE)",
                f"{rmse:.4f}"
            )

            st.caption(
                "A smaller RMSE indicates closer agreement "
                "between the model and observed readings."
            )

            st.info(
                "OD is a proxy for algal concentration. "
                "It is not automatically equivalent to dry biomass."
            )

    except ValueError:

        st.error(
            "Please enter valid numerical readings separated by commas."
        )


# ================================================================
# 15. SCIENTIFIC MODEL NOTES
# ================================================================

st.divider()

st.markdown("""
<div class="info-card">

<b>SCIENTIFIC MODEL NOTES</b><br><br>

• Light response: literature-fitted equation.<br>

• Temperature response: exploratory extension.<br>

• Photoperiod response: simplified proportional assumption.<br>

• Biomass: normalised logistic prediction.<br>

• LED power: used only for electricity calculations.<br>

• Energy efficiency: relative biomass units per kWh.<br><br>

Predictions require experimental validation.
Actual LED electricity consumption should be measured whenever possible.

</div>
""", unsafe_allow_html=True)


st.markdown("""
<p style="
    text-align:center;
    color:#78917e;
    font-size:12px;
    margin-top:35px;">
    ALGORA • MODEL-GUIDED MICROALGAE CULTIVATION
</p>
""", unsafe_allow_html=True)


# ================================================================
# END OF ALGORA v3 STREAMLIT WEBSITE
# ================================================================

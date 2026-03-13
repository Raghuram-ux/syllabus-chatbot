import streamlit as st
import re
from collections import Counter
import math
from openai import OpenAI

# ── Embedded knowledge base (RAG corpus) ──────────────────────────────────────
SYLLABUS_CHUNKS = [
    {
        "id": "ma23412-overview",
        "subject": "MA23412 Random Processes and Linear Algebra",
        "content": """Course: MA23412 RANDOM PROCESSES AND LINEAR ALGEBRA. Credits: L3 T1 P0 C4.
Objectives: Introduce probability and random variables, two-dimensional random variables and applications,
Random Processes and Limiting Distributions, vector spaces and their properties,
linear transformations, inner product spaces, and orthogonalization.""",
    },
    {
        "id": "ma23412-units",
        "subject": "MA23412 Random Processes and Linear Algebra - Units",
        "content": """Unit I RANDOM VARIABLES (9+3): Random Variable, Discrete and continuous random variables, Moments,
Moment generating functions, Binomial, Poisson, Geometric, Uniform, Exponential and Normal distributions.
Unit II TWO-DIMENSIONAL RANDOM VARIABLES (9+3): Joint distributions, Marginal and conditional distributions,
Covariance, Correlation and linear regression, Transformation of random variables, Central limit theorem.
Unit III RANDOM PROCESSES (9+3): Classification, Stationary process, Markov process, Poisson process,
Discrete parameter Markov chain, Chapman Kolmogorov equations, Limiting distributions.
Unit IV VECTOR SPACES (9+3): Vector spaces, Subspaces, Linear combinations and linear system of equations,
Linear independence and linear dependence, Bases and dimensions.
Unit V LINEAR TRANSFORMATION AND INNER PRODUCT SPACE (9+3): Linear transformation, Null spaces and ranges,
Dimension theorem, Matrix representation of linear transformations, Inner product, Norms,
Gram Schmidt orthogonalization process. Total: 60 periods.""",
    },
    {
        "id": "ma23412-outcomes",
        "subject": "MA23412 Course Outcomes",
        "content": """CO1: Know fundamental knowledge of probability concepts and standard distributions for real life phenomena.
CO2: Know basic concepts of one and two-dimensional random variables and engineering applications.
CO3: Apply testing of hypothesis for small and large samples.
CO4: Explain fundamental concepts of vector space and their role in mathematics.
CO5: Demonstrate use of inner product space and linear transformation.
Textbooks: Ibe O.C. Fundamentals of Applied Probability (Unit I-II), Gross D. Fundamentals of Queueing Theory (Unit III),
Friedberg Linear Algebra Prentice Hall 4th Ed (Unit IV-V).""",
    },
    {
        "id": "ec23411-overview",
        "subject": "EC23411 Communication Systems",
        "content": """Course: EC23411 COMMUNICATION SYSTEMS. Credits: L3 T0 P0 C3.
Objectives: Introduce amplitude modulation and demodulation, angle modulation and demodulation,
baseband signaling, source coding techniques for data compression and error correction,
digital modulation techniques and synchronization.""",
    },
    {
        "id": "ec23411-units",
        "subject": "EC23411 Communication Systems - Units",
        "content": """Unit I AMPLITUDE MODULATION (9): AM, DSB, SSB, VSB modulations. SSB Generation – Filter and Phase Shift Methods,
VSB Generation, Hilbert Transform, Pre-envelope & complex envelope, Superheterodyne Receiver, Noise in AM.
Unit II ANGLE MODULATION (9): Phase and frequency modulation, Narrow Band and Wide band FM, Modulation index,
Spectra, FM Demodulation, PLL as FM Demodulator, Pre-emphasis and De-emphasis, Noise in FM.
Unit III BASEBAND SIGNALLING (9): Low pass sampling, Aliasing, Signal Reconstruction, Quantization,
Uniform & non-uniform quantization, Logarithmic Companding, PAM, PPM, PWM, PCM, DPCM, Delta modulation,
Adaptive delta modulation.
Unit IV SOURCE CODING (9): Discrete Memoryless source, Information, Entropy, Mutual Information,
Binary Symmetric Channel, Channel Capacity, Hartley-Shannon law, Shannon-Fano & Huffman codes,
Linear Block codes, Hamming codes, Cyclic codes.
Unit V DIGITAL MODULATION (9): BASK, BFSK, BPSK, QPSK, QAM, Carrier Synchronization,
Non-coherent Receivers, DPSK. Total: 60 periods. Textbook: Simon Haykins Communication Systems 5th Ed Wiley 2009.""",
    },
    {
        "id": "ec23411-outcomes",
        "subject": "EC23411 Course Outcomes",
        "content": """CO1: Determine parameters of amplitude modulation and demodulation techniques.
CO2: Classify various angle modulation with demodulation schemes.
CO3: Summarize pulse modulation techniques for signal encoding and transmission.
CO4: Investigate source coding techniques for data compression and channel coding for reliable communication.
CO5: Find out various shift keying techniques for signal generation.""",
    },
    {
        "id": "ec23412-overview",
        "subject": "EC23412 Electromagnetic Fields",
        "content": """Course: EC23412 ELECTROMAGNETIC FIELDS. Credits: L3 T1 P0 C4.
Objectives: Expose methods of computing static electric field and magnetic field,
Faraday's law, displacement current and Maxwell equations, Time varying fields,
Electromagnetic wave propagation.""",
    },
    {
        "id": "ec23412-units",
        "subject": "EC23412 Electromagnetic Fields - Units",
        "content": """Unit I COORDINATE SYSTEMS AND VECTOR CALCULUS (12): Rectangular, Cylindrical and Spherical coordinate systems,
Differential Length Area Volume, Curl, Gradient and Divergence, Divergence theorem, Stoke's theorem.
Unit II ELECTRIC FIELD, POTENTIAL AND ENERGY (12): Coulomb's Law, Electric field intensity,
Line/surface/volume charge distributions, Gauss' law, Electric flux density, Potential, Energy in Electrostatic field.
Unit III ELECTROSTATIC BOUNDARY VALUE PROBLEMS (12): Boundary conditions in dielectrics,
Poisson and Laplace equations, Capacitance, Conductors, Current and current density.
Unit IV MAGNETOSTATICS (12): Biot-Savart's Law, Magnetic field intensity, Magnetic flux density,
Ampere's Circuital Law, Scalar and Vector Magnetic Potentials, Force and Torque, Magnetic Boundary Conditions.
Unit V TIME VARYING FIELDS AND WAVE PROPAGATION (12): Faraday's law, Displacement current,
Maxwell's equations, Poynting's theorem, Wave equations, Wave propagation in Conductors, dielectrics and free space.
Total: 60 periods. Textbook: Sadiku Principles of Electromagnetics Oxford University Press 6th Ed 2015.""",
    },
    {
        "id": "ec23413-overview",
        "subject": "EC23413 Linear Integrated Circuits",
        "content": """Course: EC23413 LINEAR INTEGRATED CIRCUITS. Credits: L3 T0 P0 C3.
Objectives: Fundamental Elements of Linear Integrated Circuits, linear and non-linear applications of op-amps,
analog multipliers and PLLs, analog-to-digital and digital-to-analog converters, waveform generators and special function ICs.""",
    },
    {
        "id": "ec23413-units",
        "subject": "EC23413 Linear Integrated Circuits - Units",
        "content": """Unit I BASICS OF OP-AMPS (9): Ideal Op-Amp, DC/AC characteristics, slew rate, open/closed loop configurations,
Current mirror, current sources, MOSFET Op-Amps.
Unit II APPLICATIONS OF OP-AMPS (9): Sign Changer, Voltage Follower, V-to-I and I-to-V converters,
adder, subtractor, Instrumentation amplifier, Integrator, Differentiator, Logarithmic amplifier,
Comparators, Schmitt trigger, Precision rectifier, Butterworth active filters.
Unit III ANALOG MULTIPLIER AND PLL (9): Gilbert Multiplier, variable transconductance, PLL analysis,
VCO, Monolithic PLL IC 565, AM/FM detection, FSK modulation, Frequency synthesizing.
Unit IV ADC AND DAC (9): D/A converter – weighted resistor, R-2R Ladder, A/D Converters – Flash,
Successive Approximation, Single/Dual Slope, Sigma-Delta converters.
Unit V WAVEFORM GENERATORS AND SPECIAL ICS (9): RC Phase shift, Wein Bridge, Multivibrators,
Triangular/Sawtooth wave generators, ICL8038, Timer IC 555, IC Voltage regulators, LDO Regulators,
MF10, Audio/Video/Isolation Amplifiers, Optocouplers. Total: 45 periods. Textbook: D.Roy Choudhry Linear Integrated Circuits New Age 2018.""",
    },
    {
        "id": "ec23431-overview",
        "subject": "EC23431 Digital Signal Processing",
        "content": """Course: EC23431 DIGITAL SIGNAL PROCESSING. Credits: L3 T0 P2 C4.
Objectives: Usage of DFT in linear filtering, IIR digital filter design, FIR digital filter design,
finite precision representation effects, DSP processor concepts and multirate signal processing.""",
    },
    {
        "id": "ec23431-units",
        "subject": "EC23431 Digital Signal Processing - Units",
        "content": """Unit I DISCRETE FOURIER TRANSFORM (9): DFT derivation from DTFT, properties, Linear filtering using DFT,
overlap save and overlap add, Radix-2 DIT FFT, DIF FFT.
Unit II IIR FILTERS (9): Butterworth and Chebyshev analog filters, IIR filter design –
Approximation of derivatives, Impulse invariance, Bilinear transformation. Direct form I/II, Cascade, parallel.
Unit III FIR FILTERS (9): Symmetric and Antisymmetric FIR, Fourier series method, Windows –
Rectangular, Hamming, Hanning, Frequency sampling. Linear phase structure.
Unit IV FINITE WORD LENGTH EFFECTS (9): Fixed/floating point representation, ADC quantization,
truncation and rounding, quantization noise, coefficient quantization, overflow, limit cycle oscillations, scaling.
Unit V DSP ARCHITECTURE (9): TMS320C6748 Processor features, Fixed/Floating-point architecture,
Table look up. Multirate: Decimation, Interpolation, Sampling rate conversion,
Multi-rate filter banks, wavelet transforms, sub-band coding and image/video processing. Total: 45+30=75 periods.""",
    },
    {
        "id": "ec23431-lab",
        "subject": "EC23431 DSP Lab Experiments",
        "content": """DSP Lab exercises (30 periods) using MATLAB/DSP Processor:
1. Generation of elementary Discrete-Time sequences
2. Linear and Circular convolutions
3. Auto correlation and Cross Correlation
4. Frequency Analysis using DFT
5. Design of FIR filters (LPF/HPF/BPF/BSF)
6. Design of Butterworth and Chebyshev IIR filters
7. Study of DSP Processor architecture
8. MAC operation using various addressing modes
9. Generation of various signals and random noise
10. FIR Filter Low pass, High pass, Band pass, Band stop
11. Butterworth and Chebyshev IIR Filters
12. Up-sampling and Down-sampling in DSP Processor.""",
    },
    {
        "id": "ec23432-overview",
        "subject": "EC23432 Networks and Security",
        "content": """Course: EC23432 NETWORKS AND SECURITY. Credits: L2 T0 P2 C3.
Objectives: Network Models, data link layer functions, routing in Network Layer,
transport layer communication and congestion control, Network Security Mechanisms.""",
    },
    {
        "id": "ec23432-units",
        "subject": "EC23432 Networks and Security - Units",
        "content": """Unit I NETWORK MODELS AND LINK LAYER (6): OSI and TCP/IP models, Addressing, Data and Signals,
Data link Layer, Error Detection and Correction.
Unit II MEDIA ACCESS AND INTERNETWORKING (6): Ethernet 802.3, Wireless LAN IEEE 802.11, Bluetooth,
IP, ICMP, Mobile IP, IPv4 address.
Unit III ROUTING (6): Unicast and Multicast Routing, Intra/Inter domain Routing, IPv6, Transition from IPv4 to IPv6.
Unit IV TRANSPORT AND APPLICATION LAYERS (6): UDP and TCP, Congestion Control (DEC bit, RED), QoS,
DNS, WWW, HTTP, Electronic Mail.
Unit V NETWORK SECURITY (6): OSI Security Architecture, Attacks, Encryption, AES, Public Key Cryptosystems,
RSA Algorithm, Hash Functions, SHA, Digital Signature. Total: 30+30=60 periods.
Textbooks: Forouzan Data Communication and Networking 5th Ed TMH 2017 (Unit I-IV),
Stallings Cryptography and Network Security 7th Ed Pearson 2017 (Unit V).""",
    },
    {
        "id": "ec23421-lab",
        "subject": "EC23421 Communication Systems Laboratory",
        "content": """Course: EC23421 COMMUNICATION SYSTEMS LABORATORY. Credits: L0 T0 P2 C1.
Experiments: AM/FM Modulator and Demodulator, Pre-Emphasis and De-Emphasis, Signal sampling,
PCM Modulation/Demodulation, PAM, PPM, PWM, Delta Modulation, Digital Modulation ASK/PSK/FSK,
Simulation of DPSK/QPSK/QAM. 30 periods total.
Outcomes: Design AM/FM/Digital Modulators, Compute sampling frequency,
Simulate functional modules of communication systems, Implement digital modulation schemes,
Apply channel coding schemes.""",
    },
    {
        "id": "ec23422-lab",
        "subject": "EC23422 Linear Integrated Circuits Laboratory",
        "content": """Course: EC23422 LINEAR INTEGRATED CIRCUITS LABORATORY. Credits: L0 T0 P2 C1.
Experiments: Inverting/Non-Inverting amplifier, RC Phase shift oscillator, Wien bridge Oscillator,
Integrator and Differentiator, Schmitt trigger, Astable/Monostable multivibrators,
Instrumentation amplifier, Active filters (LPF/HPF/BPF), PLL Characteristics,
R-2R ladder DAC, IC555 multivibrators, DC Regulated power supply LM317/LM723.
SPICE Simulation: RC Phase shift oscillator, Wien Bridge Oscillator, Integrator/Differentiator,
Schmitt trigger, Active filters, Astable/Monostable using IC555, PWM using IC555. 30 periods total.""",
    },
    {
        "id": "ec23ic2-cyber",
        "subject": "EC23IC2 Cyber Security",
        "content": """Course: EC23IC2 CYBER SECURITY. Credits: L1 C1.
Unit I Introduction to Cyber Security (5): Definition, importance, key principles and goals,
Overview of cyber threat landscape.
Unit II Threats and Vulnerabilities (5): Types of cyber threats (malware, phishing, DDoS),
Common vulnerabilities in software and networks, Risk assessment and management.
Unit III Network Security (5): Firewalls, intrusion detection and prevention systems,
Securing communication channels (VPN, TLS), Cryptography, Encryption algorithms,
Secure storage and transmission. Practical: Configuring firewalls/IDS, Simulating cyber-attacks. Total: 15 periods.
Outcomes: Protect computer systems from cybersecurity attacks, Diagnose and investigate cybersecurity events,
Communicate professionally to address information security issues.""",
    },
]

# ── Simple cosine-similarity based retriever ─────────────────────────────────
def tokenize(text):
    return re.findall(r'\b\w+\b', text.lower())

def tf_vector(tokens):
    return Counter(tokens)

def cosine_sim(a, b):
    all_keys = set(a.keys()) | set(b.keys())
    dot = sum(a.get(k, 0) * b.get(k, 0) for k in all_keys)
    mag_a = math.sqrt(sum(v**2 for v in a.values()))
    mag_b = math.sqrt(sum(v**2 for v in b.values()))
    if mag_a == 0 or mag_b == 0:
        return 0
    return dot / (mag_a * mag_b)

def retrieve_chunks(query, top_k=3):
    q_vec = tf_vector(tokenize(query))
    scored = []
    for chunk in SYLLABUS_CHUNKS:
        text = chunk['subject'] + ' ' + chunk['content']
        c_vec = tf_vector(tokenize(text))
        score = cosine_sim(q_vec, c_vec)
        scored.append((chunk, score))
    scored.sort(key=lambda x: x[1], reverse=True)
    return [chunk for chunk, _ in scored[:top_k]]

# ── API call ──────────────────────────────────────────────────────────────────
def ask_openai(query, history, api_key):
    client = OpenAI(api_key=api_key)
    relevant_chunks = retrieve_chunks(query, 4)
    context = '\n\n---\n\n'.join(f"[{c['subject']}]\n{c['content']}" for c in relevant_chunks)

    system_prompt = f"""You are a helpful academic assistant for 4th Semester ECE (Electronics and Communication Engineering) students.
Answer questions ONLY based on the syllabus information provided in the context below.
Be concise, clear, and helpful. If something is not in the context, say so honestly.
Format your answer neatly. Use bullet points for lists.

SYLLABUS CONTEXT:
{context}"""

    messages = [{"role": "system", "content": system_prompt}] + history + [{"role": "user", "content": query}]

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        max_tokens=1000,
        messages=messages,
    )

    answer = response.choices[0].message.content
    sources = [c['subject'] for c in relevant_chunks]
    return answer, sources

# ── Streamlit App ─────────────────────────────────────────────────────────────
st.set_page_config(page_title="Syllabus Chatbot", page_icon="📚")

st.title("📚 4th Semester ECE Syllabus Assistant")

# Sidebar with course list
st.sidebar.title("Courses")
courses = [
    {"code": "MA23412", "name": "Random Processes & Linear Algebra", "color": "#6366f1"},
    {"code": "EC23411", "name": "Communication Systems", "color": "#0ea5e9"},
    {"code": "EC23412", "name": "Electromagnetic Fields", "color": "#10b981"},
    {"code": "EC23413", "name": "Linear Integrated Circuits", "color": "#f59e0b"},
    {"code": "EC23431", "name": "Digital Signal Processing", "color": "#ec4899"},
    {"code": "EC23432", "name": "Networks & Security", "color": "#8b5cf6"},
    {"code": "EC23421", "name": "Communication Lab", "color": "#14b8a6"},
    {"code": "EC23422", "name": "LIC Lab", "color": "#f97316"},
    {"code": "EC23IC2", "name": "Cyber Security", "color": "#ef4444"},
]

for course in courses:
    st.sidebar.markdown(f'<div style="background-color:{course["color"]}; padding:5px; border-radius:5px; margin:2px 0;"><strong>{course["code"]}</strong><br/>{course["name"]}</div>', unsafe_allow_html=True)

# Get API key from secrets or environment
import os
api_key = None
if "OPENAI_API_KEY" in os.environ:
    api_key = os.environ["OPENAI_API_KEY"]
else:
    try:
        api_key = st.secrets["OPENAI_API_KEY"]
    except KeyError:
        pass

if not api_key:
    st.error("OpenAI API key not found. Please set OPENAI_API_KEY environment variable or add it to Streamlit secrets.")
    st.stop()

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "👋 Hello! I'm your **4th Semester ECE Syllabus Assistant**. Ask me anything about your courses — units, outcomes, textbooks, lab experiments, or credit structure!", "sources": []}
    ]

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message["sources"]:
            st.markdown("**Sources:** " + ", ".join(message["sources"]))

# Chat input
if prompt := st.chat_input("Ask about your syllabus..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt, "sources": []})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get assistant response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                history = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages[:-1] if m["role"] != "system"]
                answer, sources = ask_openai(prompt, history, api_key)
                st.markdown(answer)
                if sources:
                    st.markdown("**Sources:** " + ", ".join(sources))
                st.session_state.messages.append({"role": "assistant", "content": answer, "sources": sources})
            except Exception as e:
                error_msg = f"⚠️ Error: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg, "sources": []})
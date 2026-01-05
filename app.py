"""
MAD System - Multi-Agent Debate Streamlit Interface
"""
import streamlit as st
from workflows.debate_flow import run_debate
import config

# Page configuration
st.set_page_config(
    page_title="MAD - Multi-Agent Debate System",
    page_icon="🎭",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        background: linear-gradient(90deg, #1E3A5F, #2E5A8F);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #666;
        margin-top: 5px;
    }
    .info-box {
        background: linear-gradient(135deg, #f5f7fa 0%, #e4e8ec 100%);
        border-radius: 12px;
        padding: 20px;
        margin: 15px 0;
    }
    .agent-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 500;
        margin: 3px;
    }
    .advocate-badge { background: #d4edda; color: #155724; }
    .critic-badge { background: #f8d7da; color: #721c24; }
    .contrarian-badge { background: #fff3cd; color: #856404; }
    .expert-badge { background: #e2d5f1; color: #4a235a; }
    .synthesizer-badge { background: #d1ecf1; color: #0c5460; }
    .judge-badge { background: #d6d8db; color: #1b1e21; }
    .step-number {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 28px;
        height: 28px;
        background: #1E3A5F;
        color: white;
        border-radius: 50%;
        font-weight: bold;
        margin-right: 10px;
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# SIDEBAR - Clean Settings
# ============================================
with st.sidebar:
    st.markdown("### ⚙️ Settings")

    domain = st.text_input(
        "Domain Context",
        value="general business strategy",
        help="Optional: Specify a domain (e.g., 'healthcare', 'fintech', 'retail')"
    )

    st.markdown("---")
    st.markdown("### 🔧 Technical Info")

    with st.expander("View Active Models", expanded=False):
        for agent, settings in config.AGENT_MODELS.items():
            if agent != "domain_expert" or config.DEBATE_CONFIG.get("enable_domain_expert"):
                st.caption(f"**{agent.replace('_', ' ').title()}**")
                st.code(f"{settings['provider']}/{settings['model']}", language=None)

# ============================================
# MAIN CONTENT
# ============================================

# Header
st.markdown('<p class="main-header">🎭 Multi-Agent Debate System</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Get diverse AI perspectives on strategic decisions — not just one opinion</p>', unsafe_allow_html=True)

# Create tabs for main navigation
main_tab1, main_tab2 = st.tabs(["💬 Start a Debate", "ℹ️ How It Works"])

# ============================================
# TAB 1: DEBATE INTERFACE
# ============================================
with main_tab1:
    st.markdown("### What decision are you facing?")

    question = st.text_area(
        "Enter your strategic question",
        placeholder="Example: Should we expand into the European market this year, or focus on strengthening our US presence first?",
        height=100,
        label_visibility="collapsed"
    )

    # Example questions
    with st.expander("💡 Example questions to try"):
        st.markdown("""
        - *Should we build our own AI solution or buy an existing one?*
        - *Is now the right time to raise funding, or should we bootstrap longer?*
        - *Should we prioritize mobile app development or focus on web first?*
        - *Should we hire specialists or train our existing team?*
        - *Is vertical integration the right strategy for our supply chain?*
        """)

    # Start button
    if st.button("🚀 Start Debate", type="primary", use_container_width=True):
        if not question.strip():
            st.error("Please enter a question first.")
        else:
            progress_bar = st.progress(0)
            status_text = st.empty()

            def update_progress(step_name, description):
                steps = {
                    "Round 1 Complete": 25,
                    "Round 2 Complete": 50,
                    "Round 3 Complete": 65,
                    "Synthesis Complete": 85,
                    "Judgment Complete": 100
                }
                progress = steps.get(step_name, 0)
                progress_bar.progress(progress)
                status_text.info(f"⏳ {description}")

            try:
                with st.spinner("🎭 AI agents are debating your question... This takes 2-4 minutes."):
                    results = run_debate(
                        question=question,
                        domain=domain,
                        on_step_complete=update_progress
                    )

                status_text.empty()
                progress_bar.empty()
                st.success("✅ Debate Complete! Review the results below.")

                # Results tabs
                result_tab1, result_tab2, result_tab3, result_tab4 = st.tabs([
                    "📋 Executive Summary",
                    "💬 Full Debate",
                    "🎯 Strategic Options",
                    "⚖️ Final Verdict"
                ])

                with result_tab1:
                    st.markdown("### Your Question")
                    st.info(results["question"])

                    st.markdown("### Key Takeaways")
                    judgment = results.get("judgment", "")
                    # Show first portion of judgment as summary
                    if len(judgment) > 2000:
                        st.markdown(judgment[:2000] + "...")
                        st.caption("*See 'Final Verdict' tab for complete analysis*")
                    else:
                        st.markdown(judgment)

                with result_tab2:
                    st.markdown("### Complete Debate Transcript")
                    st.caption("Click each section to expand and read the full argument.")

                    for round_data in results.get("rounds", []):
                        st.markdown(f"#### Round {round_data['round']}: {round_data['phase']}")

                        if "advocate" in round_data:
                            with st.expander("🟢 **Advocate** — The case FOR your proposal"):
                                st.markdown(round_data["advocate"])

                        if "critic" in round_data:
                            with st.expander("🔴 **Critic** — Risks and concerns"):
                                st.markdown(round_data["critic"])

                        if "contrarian" in round_data:
                            with st.expander("🟠 **Contrarian** — Alternative approaches"):
                                st.markdown(round_data["contrarian"])

                        if "advocate_response" in round_data:
                            with st.expander("🟢 **Advocate Response** — Addressing concerns"):
                                st.markdown(round_data["advocate_response"])

                        if "critic_response" in round_data:
                            with st.expander("🔴 **Critic Response** — Final assessment"):
                                st.markdown(round_data["critic_response"])

                        if "domain_expert" in round_data:
                            with st.expander("🟣 **Domain Expert** — Reality check"):
                                st.markdown(round_data["domain_expert"])

                        st.markdown("---")

                with result_tab3:
                    st.markdown("### Synthesized Strategic Options")
                    st.caption("The best ideas from all perspectives, combined into actionable options.")
                    st.markdown(results.get("synthesis", "No synthesis available"))

                with result_tab4:
                    st.markdown("### Final Judgment")
                    st.caption("An impartial evaluation of all arguments and a recommendation.")
                    st.markdown(results.get("judgment", "No judgment available"))

            except Exception as e:
                st.error(f"Something went wrong: {str(e)}")
                with st.expander("Technical details"):
                    st.exception(e)

# ============================================
# TAB 2: HOW IT WORKS
# ============================================
with main_tab2:
    st.markdown("## What is the Multi-Agent Debate System?")

    st.markdown("""
    <div class="info-box">
    <p><strong>The Problem:</strong> When you ask ChatGPT, Claude, or any AI a question, you get <em>one perspective</em>.
    Research shows that all major AI models tend to give similar answers — they've all been trained to be helpful and agreeable,
    which means you often get a "safe" consensus view rather than truly diverse thinking.</p>

    <p><strong>The Solution:</strong> This system makes <em>multiple AI agents debate each other</em>, each playing a different role.
    Instead of one AI trying to give you a balanced answer, you get genuine intellectual conflict — arguments, counterarguments,
    and alternatives you might never have considered.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("## Meet the Debate Team")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        #### 🟢 The Advocate
        **Role:** Builds the strongest possible case FOR your idea

        Like a skilled lawyer, this agent finds every reason why your proposal makes sense.
        It identifies opportunities, marshals evidence, and anticipates objections.

        ---

        #### 🔴 The Critic
        **Role:** Stress-tests your idea and finds weaknesses

        This agent has seen countless initiatives fail. It identifies hidden assumptions,
        potential failure points, and asks the hard questions others avoid.

        ---

        #### 🟠 The Contrarian
        **Role:** Proposes alternatives you haven't considered

        "What if we're solving the wrong problem?" This agent challenges conventional thinking
        and brings ideas from other industries or approaches.
        """)

    with col2:
        st.markdown("""
        #### 🟣 The Domain Expert
        **Role:** Grounds the debate in real-world constraints

        Every industry has unwritten rules. This agent brings practical knowledge about
        regulations, stakeholder dynamics, and implementation realities.

        ---

        #### 🔵 The Synthesizer
        **Role:** Combines the best ideas into clear options

        After the debate, this agent identifies where everyone agrees, where they genuinely
        disagree, and crafts 2-4 distinct strategic options with clear trade-offs.

        ---

        #### ⚫ The Judge
        **Role:** Evaluates arguments and gives a final verdict

        An impartial arbiter who scores each argument on logic and evidence.
        Tells you which points survived scrutiny and what remains uncertain.
        """)

    st.markdown("---")
    st.markdown("## How the Debate Works")

    st.markdown("""
    <div style="margin: 20px 0;">
        <p><span class="step-number">1</span><strong>You ask a question</strong> — Any strategic decision you're facing</p>
        <p><span class="step-number">2</span><strong>Round 1: Opening arguments</strong> — Advocate, Critic, and Contrarian share initial positions</p>
        <p><span class="step-number">3</span><strong>Round 2: Cross-examination</strong> — Agents respond to each other's arguments</p>
        <p><span class="step-number">4</span><strong>Reality check</strong> — Domain Expert grounds everything in practical constraints</p>
        <p><span class="step-number">5</span><strong>Synthesis</strong> — Best ideas combined into actionable options</p>
        <p><span class="step-number">6</span><strong>Final verdict</strong> — Judge evaluates and recommends</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("## When to Use This")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        #### ✅ Great for:
        - Major strategic decisions
        - "Should we X or Y?" questions
        - Investment or resource allocation
        - Market entry decisions
        - Build vs. buy decisions
        - Hiring and team structure
        - Product strategy
        """)

    with col2:
        st.markdown("""
        #### ❌ Not ideal for:
        - Simple factual questions
        - Tasks with one right answer
        - Urgent decisions (takes 2-4 min)
        - Highly technical implementation details
        - Personal life advice
        """)

    st.markdown("---")
    st.info("💡 **Tip:** The more context you provide in your question, the better the debate. Instead of 'Should we expand?', try 'Should we expand into European markets this year, given our current team of 50 and $2M runway?'")

# Footer
st.markdown("---")
st.caption("MAD System v1.0 — Breaking the AI Hivemind through structured adversarial debate")

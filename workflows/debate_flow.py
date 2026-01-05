"""
Debate Flow Orchestrator
Manages the multi-agent debate workflow using CrewAI
"""
from crewai import Task, Crew, Process
from typing import Optional, Callable

from agents import (
    create_advocate_agent,
    create_critic_agent,
    create_contrarian_agent,
    create_domain_expert_agent,
    create_synthesizer_agent,
    create_judge_agent
)
import config


def run_debate(
    question: str,
    domain: str = "general business strategy",
    on_step_complete: Optional[Callable[[str, str], None]] = None
) -> dict:
    """
    Run a full multi-agent debate on a strategic question.

    Args:
        question: The strategic question to debate
        domain: Domain context for the domain expert
        on_step_complete: Optional callback(agent_name, output) called after each step

    Returns:
        Dictionary containing all debate outputs and final synthesis
    """
    results = {
        "question": question,
        "domain": domain,
        "rounds": []
    }

    # Create all agents
    advocate = create_advocate_agent()
    critic = create_critic_agent()
    contrarian = create_contrarian_agent()
    domain_expert = create_domain_expert_agent(domain)
    synthesizer = create_synthesizer_agent()
    judge = create_judge_agent()

    # ============================================
    # ROUND 1: Initial Positions (Parallel)
    # ============================================

    # Task 1: Advocate's initial position
    advocate_task = Task(
        description=f"""
        Analyze the following strategic question and build the strongest possible case FOR it:

        QUESTION: {question}

        Follow your output format strictly:
        (1) THESIS: One-sentence summary of your position
        (2) STRATEGIC CASE: 3-5 major arguments with evidence
        (3) ANTICIPATED OBJECTIONS: Top 2-3 objections and your preemptive rebuttals
        (4) CALL TO ACTION: What specific next step this analysis supports
        """,
        expected_output="A compelling, evidence-based case FOR the proposal",
        agent=advocate
    )

    # Task 2: Critic's initial position
    critic_task = Task(
        description=f"""
        Analyze the following strategic question and identify all weaknesses, risks, and failure modes:

        QUESTION: {question}

        Follow your output format strictly:
        (1) CRITICAL THESIS: One-sentence summary of your primary concern
        (2) KEY VULNERABILITIES: 3-5 specific weaknesses ranked by severity
        (3) FAILURE SCENARIOS: 2-3 concrete 'If X, then Y' failure paths
        (4) BURDEN OF PROOF: What evidence would be required to address your concerns
        """,
        expected_output="A thorough risk analysis with specific failure scenarios",
        agent=critic
    )

    # Task 3: Contrarian's alternative approaches
    contrarian_task = Task(
        description=f"""
        Analyze the following strategic question and propose genuinely different alternative approaches:

        QUESTION: {question}

        Follow your output format strictly:
        (1) REFRAME: How might we think about this problem differently?
        (2) ALTERNATIVE APPROACHES: 2-3 genuinely different paths with rationale
        (3) HYBRID POSSIBILITIES: Elements that could be combined with the original proposal
        (4) UNEXPLORED QUESTIONS: What questions should we be asking that we aren't?
        """,
        expected_output="Alternative approaches and reframing of the problem",
        agent=contrarian
    )

    # Run Round 1: Initial positions (parallel execution)
    round1_crew = Crew(
        agents=[advocate, critic, contrarian],
        tasks=[advocate_task, critic_task, contrarian_task],
        process=Process.sequential,  # CrewAI handles parallel internally
        verbose=config.DEBATE_CONFIG["verbose"]
    )

    round1_results = round1_crew.kickoff()

    # Store round 1 results
    round1_output = {
        "round": 1,
        "phase": "Initial Positions",
        "advocate": str(round1_results.tasks_output[0]) if round1_results.tasks_output else "",
        "critic": str(round1_results.tasks_output[1]) if len(round1_results.tasks_output) > 1 else "",
        "contrarian": str(round1_results.tasks_output[2]) if len(round1_results.tasks_output) > 2 else ""
    }
    results["rounds"].append(round1_output)

    if on_step_complete:
        on_step_complete("Round 1 Complete", "Initial positions from Advocate, Critic, and Contrarian")

    # ============================================
    # ROUND 2: Adversarial Responses
    # ============================================

    debate_context = f"""
    ORIGINAL QUESTION: {question}

    ADVOCATE'S POSITION:
    {round1_output['advocate']}

    CRITIC'S ANALYSIS:
    {round1_output['critic']}

    CONTRARIAN'S ALTERNATIVES:
    {round1_output['contrarian']}
    """

    # Advocate responds to criticism
    advocate_response_task = Task(
        description=f"""
        Review the debate so far and respond to the Critic's concerns and Contrarian's alternatives:

        {debate_context}

        Address the Critic's key vulnerabilities and explain why the proposed approach is still superior
        to the Contrarian's alternatives. Acknowledge valid points but defend your core thesis.
        """,
        expected_output="Rebuttal addressing criticism while maintaining core argument",
        agent=advocate
    )

    # Critic responds to advocate's rebuttals
    critic_response_task = Task(
        description=f"""
        Review the debate so far and evaluate whether your concerns have been adequately addressed:

        {debate_context}

        Assess whether the Advocate's arguments hold up to scrutiny. Acknowledge what they got right,
        but press on remaining weaknesses. Consider if the Contrarian's alternatives address your concerns better.
        """,
        expected_output="Evaluation of rebuttals and remaining concerns",
        agent=critic
    )

    round2_crew = Crew(
        agents=[advocate, critic],
        tasks=[advocate_response_task, critic_response_task],
        process=Process.sequential,
        verbose=config.DEBATE_CONFIG["verbose"]
    )

    round2_results = round2_crew.kickoff()

    round2_output = {
        "round": 2,
        "phase": "Adversarial Responses",
        "advocate_response": str(round2_results.tasks_output[0]) if round2_results.tasks_output else "",
        "critic_response": str(round2_results.tasks_output[1]) if len(round2_results.tasks_output) > 1 else ""
    }
    results["rounds"].append(round2_output)

    if on_step_complete:
        on_step_complete("Round 2 Complete", "Adversarial responses exchanged")

    # ============================================
    # ROUND 3: Domain Expert Reality Check
    # ============================================

    if config.DEBATE_CONFIG["enable_domain_expert"]:
        full_debate_context = f"""
        {debate_context}

        ADVOCATE'S RESPONSE TO CRITICISM:
        {round2_output['advocate_response']}

        CRITIC'S FOLLOW-UP:
        {round2_output['critic_response']}
        """

        domain_expert_task = Task(
            description=f"""
            Review the entire debate and provide domain-specific grounding:

            {full_debate_context}

            As a domain expert in {domain}, provide:
            (1) DOMAIN CONTEXT: Key facts the debate must account for
            (2) REGULATORY CONSIDERATIONS: What compliance/regulatory factors apply
            (3) IMPLEMENTATION REALITIES: What the debate is getting right/wrong about feasibility
            (4) PRECEDENTS: Relevant examples from this domain with lessons
            (5) CRITICAL DEPENDENCIES: What must be true for any approach to succeed
            """,
            expected_output="Domain-grounded reality check on the debate",
            agent=domain_expert
        )

        domain_crew = Crew(
            agents=[domain_expert],
            tasks=[domain_expert_task],
            process=Process.sequential,
            verbose=config.DEBATE_CONFIG["verbose"]
        )

        domain_results = domain_crew.kickoff()

        round3_output = {
            "round": 3,
            "phase": "Domain Expert Reality Check",
            "domain_expert": str(domain_results.tasks_output[0]) if domain_results.tasks_output else ""
        }
        results["rounds"].append(round3_output)

        if on_step_complete:
            on_step_complete("Round 3 Complete", "Domain expert provided reality check")

    # ============================================
    # SYNTHESIS PHASE
    # ============================================

    all_debate_content = f"""
    ORIGINAL QUESTION: {question}

    === ROUND 1: INITIAL POSITIONS ===

    ADVOCATE:
    {round1_output['advocate']}

    CRITIC:
    {round1_output['critic']}

    CONTRARIAN:
    {round1_output['contrarian']}

    === ROUND 2: ADVERSARIAL EXCHANGE ===

    ADVOCATE RESPONSE:
    {round2_output['advocate_response']}

    CRITIC RESPONSE:
    {round2_output['critic_response']}
    """

    if config.DEBATE_CONFIG["enable_domain_expert"]:
        all_debate_content += f"""
    === ROUND 3: DOMAIN EXPERT ===

    {results['rounds'][-1].get('domain_expert', '')}
        """

    synthesizer_task = Task(
        description=f"""
        Synthesize the entire debate into actionable strategic options:

        {all_debate_content}

        Provide:
        (1) CONVERGENCE POINTS: Where all/most perspectives agreed
        (2) PRODUCTIVE TENSIONS: Genuine disagreements representing real trade-offs
        (3) STRATEGIC OPTIONS: 2-4 distinct approaches synthesized from the debate
        (4) DECISION CRITERIA: Framework for choosing between options
        (5) OPEN QUESTIONS: What remains unresolved
        """,
        expected_output="Synthesized strategic options with clear trade-offs",
        agent=synthesizer
    )

    synthesis_crew = Crew(
        agents=[synthesizer],
        tasks=[synthesizer_task],
        process=Process.sequential,
        verbose=config.DEBATE_CONFIG["verbose"]
    )

    synthesis_results = synthesis_crew.kickoff()

    results["synthesis"] = str(synthesis_results.tasks_output[0]) if synthesis_results.tasks_output else ""

    if on_step_complete:
        on_step_complete("Synthesis Complete", "Options synthesized from debate")

    # ============================================
    # JUDGMENT PHASE
    # ============================================

    final_context = f"""
    {all_debate_content}

    === SYNTHESIS ===

    {results['synthesis']}
    """

    judge_task = Task(
        description=f"""
        Evaluate the entire debate and synthesis, then provide your final assessment:

        {final_context}

        Provide:
        (1) EXECUTIVE ASSESSMENT: 2-3 sentence summary of what this debate revealed
        (2) ARGUMENT SCORECARD: Which arguments survived/failed scrutiny
        (3) EVIDENCE QUALITY: What was well-supported vs. speculative
        (4) REMAINING UNCERTAINTIES: What we still don't know (ranked by importance)
        (5) DECISION READINESS: Is this ready for decision? If not, what's needed?
        (6) RECOMMENDATION: Your advised course of action (clearly marked as opinion)
        """,
        expected_output="Final judgment and recommendation for the decision-maker",
        agent=judge
    )

    judge_crew = Crew(
        agents=[judge],
        tasks=[judge_task],
        process=Process.sequential,
        verbose=config.DEBATE_CONFIG["verbose"]
    )

    judge_results = judge_crew.kickoff()

    results["judgment"] = str(judge_results.tasks_output[0]) if judge_results.tasks_output else ""

    if on_step_complete:
        on_step_complete("Judgment Complete", "Final assessment delivered")

    return results

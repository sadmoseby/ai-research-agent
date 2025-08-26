# Conditional Restart Logic Implementation

## Summary

The research agent workflow has been enhanced with conditional restart logic that automatically restarts the planning phase when:

1. **Significant prior art is discovered** (3+ similar implementations)
2. **Low viability scores are received** (<51/100 from criticism analysis)

This ensures higher quality research outputs by iteratively refining approaches when issues are identified.

## Key Features

### Automatic Quality Control

- **Prior Art Check**: Prevents pursuing ideas with too much existing competition
- **Viability Assessment**: Prevents proceeding with fundamentally flawed approaches
- **Iteration Limits**: Maximum 3 planning cycles to prevent infinite loops

### Intelligent Restart Guidance

- **Differentiation Focus**: When prior art found, guides toward novel approaches
- **Risk Mitigation**: When viability low, guides toward addressing identified concerns
- **Enhanced Search**: Additional search queries in subsequent iterations

### Scoring System

- **0-30**: Major flaws - likely restart
- **31-50**: Significant concerns - likely restart
- **51-70**: Moderate concerns - proceed with caution
- **71-85**: Good concept - minor refinements
- **86-100**: Excellent concept - minimal issues

## Technical Implementation

### State Management

New fields added to `ResearchState`:

```python
criticism_score: Optional[float]
should_restart_planning: bool
restart_reason: Optional[str]
planning_iteration: int
```

### Conditional Routing

```
plan → web_research → prior_art ──┐
  ↑                                │
  │  if substantial prior art      ↓
  └────────────────────────────────●
                                   │
                                   ↓
                               criticism ──┐
  ↑                                       │
  │  if low viability score               ↓
  └───────────────────────────────────────●
                                          │
                                          ↓
                                    synthesize → validate → persist
```

### Configuration Constants

```python
MIN_VIABILITY_SCORE = 51      # Minimum score to proceed
MAX_PLANNING_ITERATIONS = 3   # Maximum restart attempts
PRIOR_ART_THRESHOLD = 3       # Prior art count triggering restart
```

## Node Changes

### `plan.py`

- Tracks planning iterations
- Provides restart-specific guidance
- Adds varied search queries for iterations
- Clears restart flags

### `prior_art.py`

- Evaluates prior art significance
- Sets restart conditions
- Routes conditionally to plan or criticism

### `criticism.py`

- Extracts viability scores from criticism text
- Evaluates restart necessity
- Routes conditionally to plan or synthesize

### `graph.py`

- Implements conditional edges
- Routes based on restart flags
- Maintains validation retry logic

## Benefits

1. **Higher Quality**: Automatically identifies and addresses fundamental issues
2. **Efficiency**: Prevents time waste on flawed approaches
3. **Novelty**: Encourages unique approaches when prior art exists
4. **Robustness**: Multiple quality checkpoints throughout workflow
5. **Learning**: Iterative refinement improves understanding

## Usage Examples

### Prior Art Restart

```
Iteration 1: "momentum trading strategy"
→ Finds 5 similar implementations
→ Restart with guidance: "Focus on novel approaches, unique data sources"

Iteration 2: "momentum trading with alternative data sentiment"
→ Fewer similar implementations found
→ Proceed to criticism
```

### Viability Restart

```
Iteration 1: "predict stock prices with astrology"
→ Criticism score: 15/100 (major flaws)
→ Restart with guidance: "Focus on risk mitigation, feasible approaches"

Iteration 2: "technical analysis with astronomical cycle correlation"
→ Criticism score: 45/100 (still concerns)
→ Restart with more guidance

Iteration 3: "sector rotation based on economic cycles"
→ Criticism score: 72/100 (viable)
→ Proceed to synthesis
```

## Testing

Comprehensive test suite validates:

- Prior art restart conditions
- Criticism score thresholds
- Score extraction from text
- Iteration limit enforcement
- Configuration constants

Run tests with:

```bash
python3 test_restart_logic.py
```

## Future Enhancements

- **Weighted Scoring**: More sophisticated scoring algorithms
- **Domain-Specific Thresholds**: Different standards for different strategy types
- **User Feedback**: Allow manual restart decisions
- **Historical Learning**: Improve restart logic based on past outcomes
- **Performance Metrics**: Track restart effectiveness

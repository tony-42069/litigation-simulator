# Litigation Simulator Database Schema

This document defines the PostgreSQL database schema for the Litigation Simulator application. The schema is designed to support the application's core functionalities including judge analysis, case prediction, and interactive simulations.

## Tables Overview

1. Users - Application users
2. Judges - Judge profiles and metadata
3. JudgeAnalytics - Analysis data for judges
4. Cases - Case data from Court Listener
5. Opinions - Legal opinions authored by judges
6. OralArguments - Oral argument recordings and transcripts
7. JudgePatterns - Analysis of judge questioning patterns
8. CasePredictions - Stored case outcome predictions
9. SimulationSessions - Active and completed simulation sessions
10. SimulationQuestions - Generated questions for simulations
11. SimulationResponses - User responses to simulation questions
12. SimulationFeedback - Feedback on user responses

## Schema Details

### Users

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    organization VARCHAR(100),
    role VARCHAR(20) DEFAULT 'user',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_login TIMESTAMP WITH TIME ZONE,
    subscription_tier VARCHAR(20) DEFAULT 'basic',
    subscription_expires TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT TRUE
);
```

### Judges

```sql
CREATE TABLE judges (
    id VARCHAR(36) PRIMARY KEY,  -- Court Listener ID
    name VARCHAR(100) NOT NULL,
    position VARCHAR(100),
    court VARCHAR(100),
    court_id VARCHAR(36),  -- Court Listener Court ID
    appointed_date DATE,
    birth_year INTEGER,
    education TEXT,
    prior_positions TEXT,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### JudgeAnalytics

```sql
CREATE TABLE judge_analytics (
    id SERIAL PRIMARY KEY,
    judge_id VARCHAR(36) REFERENCES judges(id),
    analysis_type VARCHAR(50) NOT NULL,  -- e.g., 'writing_style', 'topic', 'ruling_pattern'
    analysis_data JSONB NOT NULL,
    confidence FLOAT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE (judge_id, analysis_type)
);
```

### Cases

```sql
CREATE TABLE cases (
    id VARCHAR(36) PRIMARY KEY,  -- Court Listener ID
    case_name VARCHAR(255) NOT NULL,
    docket_number VARCHAR(100),
    court VARCHAR(100),
    court_id VARCHAR(36),  -- Court Listener Court ID
    date_filed DATE,
    date_terminated DATE,
    nature_of_suit VARCHAR(100),
    case_type VARCHAR(50),
    judges JSONB,  -- Array of judge IDs involved
    status VARCHAR(50),
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### Opinions

```sql
CREATE TABLE opinions (
    id VARCHAR(36) PRIMARY KEY,  -- Court Listener ID
    case_id VARCHAR(36) REFERENCES cases(id),
    author_id VARCHAR(36) REFERENCES judges(id),
    date_filed DATE,
    type VARCHAR(50),  -- e.g., 'majority', 'dissent', 'concurrence'
    text TEXT,
    text_length INTEGER,
    citation VARCHAR(255),
    precedential BOOLEAN,
    citation_count INTEGER,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX opinions_author_id_idx ON opinions(author_id);
CREATE INDEX opinions_case_id_idx ON opinions(case_id);
```

### OralArguments

```sql
CREATE TABLE oral_arguments (
    id VARCHAR(36) PRIMARY KEY,  -- Court Listener ID
    case_id VARCHAR(36) REFERENCES cases(id),
    date_argued DATE,
    duration INTEGER,  -- in seconds
    panel JSONB,  -- Array of judge IDs
    transcript TEXT,
    audio_url VARCHAR(255),
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX oral_arguments_case_id_idx ON oral_arguments(case_id);
```

### JudgePatterns

```sql
CREATE TABLE judge_patterns (
    id SERIAL PRIMARY KEY,
    judge_id VARCHAR(36) REFERENCES judges(id),
    pattern_type VARCHAR(50) NOT NULL,  -- e.g., 'questioning', 'citation', 'reasoning'
    pattern_data JSONB NOT NULL,
    source_count INTEGER,  -- Number of opinions/arguments used for analysis
    confidence FLOAT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE (judge_id, pattern_type)
);
```

### CasePredictions

```sql
CREATE TABLE case_predictions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    case_type VARCHAR(50) NOT NULL,
    case_facts TEXT NOT NULL,
    jurisdiction JSONB NOT NULL,
    judge_id VARCHAR(36) REFERENCES judges(id),
    precedent_strength FLOAT,
    input_parameters JSONB,
    predicted_outcome VARCHAR(50) NOT NULL,
    confidence FLOAT NOT NULL,
    class_probabilities JSONB,
    feature_impact JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX case_predictions_user_id_idx ON case_predictions(user_id);
```

### SimulationSessions

```sql
CREATE TABLE simulation_sessions (
    id VARCHAR(36) PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    case_type VARCHAR(50) NOT NULL,
    case_facts TEXT NOT NULL,
    jurisdiction JSONB NOT NULL,
    judge_id VARCHAR(36) REFERENCES judges(id),
    rounds_completed INTEGER DEFAULT 0,
    status VARCHAR(20) DEFAULT 'active',  -- 'active', 'completed', 'abandoned'
    metrics JSONB,  -- Aggregated performance metrics
    feedback TEXT,  -- Overall session feedback
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX simulation_sessions_user_id_idx ON simulation_sessions(user_id);
```

### SimulationQuestions

```sql
CREATE TABLE simulation_questions (
    id SERIAL PRIMARY KEY,
    simulation_id VARCHAR(36) REFERENCES simulation_sessions(id),
    question_text TEXT NOT NULL,
    category VARCHAR(50) NOT NULL,  -- e.g., 'factual', 'legal', 'hypothetical', 'challenging'
    source_pattern VARCHAR(36),  -- Reference to judge pattern if applicable
    round INTEGER NOT NULL,  -- Round number within the simulation
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX simulation_questions_simulation_id_idx ON simulation_questions(simulation_id);
```

### SimulationResponses

```sql
CREATE TABLE simulation_responses (
    id SERIAL PRIMARY KEY,
    simulation_id VARCHAR(36) REFERENCES simulation_sessions(id),
    question_id INTEGER REFERENCES simulation_questions(id),
    response_text TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX simulation_responses_question_id_idx ON simulation_responses(question_id);
CREATE INDEX simulation_responses_simulation_id_idx ON simulation_responses(simulation_id);
```

### SimulationFeedback

```sql
CREATE TABLE simulation_feedback (
    id SERIAL PRIMARY KEY,
    simulation_id VARCHAR(36) REFERENCES simulation_sessions(id),
    response_id INTEGER REFERENCES simulation_responses(id),
    metrics JSONB NOT NULL,  -- e.g., directness, persuasiveness, legal_soundness, etc.
    feedback_text TEXT NOT NULL,
    strengths JSONB,  -- Array of identified strengths
    improvements JSONB,  -- Array of areas for improvement
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX simulation_feedback_response_id_idx ON simulation_feedback(response_id);
CREATE INDEX simulation_feedback_simulation_id_idx ON simulation_feedback(simulation_id);
```

## Relationships

- Judges can author multiple Opinions
- Judges can participate in multiple OralArguments (as panel members)
- Judges have analytical data in JudgeAnalytics and JudgePatterns
- Cases can have multiple Opinions and a single OralArgument
- Users can create multiple CasePredictions and SimulationSessions
- SimulationSessions have multiple SimulationQuestions
- SimulationQuestions have corresponding SimulationResponses and SimulationFeedback

## Data Flow

1. Judge data is imported from Court Listener API and stored in Judges table
2. Opinions and OralArguments are imported and linked to Judges and Cases
3. Analysis is performed on Opinions and OralArguments to create JudgeAnalytics and JudgePatterns
4. Users interact with the system to create CasePredictions based on case details
5. Users create SimulationSessions, which generate SimulationQuestions based on JudgePatterns
6. Users provide SimulationResponses to questions, which receive SimulationFeedback

## Indexes

Indexes are created on foreign keys and frequently queried columns to optimize performance:

- User ID in case predictions and simulation sessions
- Judge ID in opinions
- Case ID in opinions and oral arguments
- Simulation ID in questions, responses, and feedback
- Question ID in responses

## Data Types

- VARCHAR for short text fields with known maximum lengths
- TEXT for longer text content like opinions and case facts
- JSONB for flexible structured data (allows indexing and querying of JSON fields)
- TIMESTAMP WITH TIME ZONE for all date/time fields to handle timezone differences
- FLOAT for confidence scores and other numeric measurements
- BOOLEAN for true/false flags
- INTEGER for counts and numeric IDs
- VARCHAR(36) for Court Listener UUIDs

## Notes

- The schema is designed to accommodate data from Court Listener while adding application-specific tables for analysis and simulation.
- JSONB fields provide flexibility for storing complex data structures without requiring schema changes.
- Timestamps include timezone information to ensure consistent time representation across different regions.
- Appropriate indexes are added to improve query performance on commonly joined fields.

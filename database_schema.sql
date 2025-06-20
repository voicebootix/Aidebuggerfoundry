-- AI Debugger Factory - Complete Database Schema
-- Production-ready PostgreSQL schema with all revolutionary features

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "citext";

-- ==========================================
-- USERS & AUTHENTICATION
-- ==========================================

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email CITEXT UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    founder_type VARCHAR(50) DEFAULT 'unknown', -- 'technical', 'business', 'hybrid'
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    github_username VARCHAR(255),
    github_token_encrypted TEXT,
    preferences JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- User indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_founder_type ON users(founder_type);
CREATE INDEX idx_users_created_at ON users(created_at);

-- ==========================================
-- VOICE CONVERSATIONS (Revolutionary Feature)
-- ==========================================

CREATE TABLE voice_conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id VARCHAR(255) UNIQUE NOT NULL,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    conversation_history JSONB NOT NULL DEFAULT '[]',
    founder_type_detected VARCHAR(50),
    business_validation_requested BOOLEAN DEFAULT FALSE,
    strategy_validated BOOLEAN DEFAULT FALSE,
    founder_ai_agreement JSONB,
    conversation_state VARCHAR(50) DEFAULT 'active', -- 'discovery', 'validation', 'strategy', 'agreement', 'code_generation', 'completed'
    voice_language VARCHAR(10) DEFAULT 'en',
    total_messages INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Voice conversation indexes
CREATE INDEX idx_voice_conversations_session_id ON voice_conversations(session_id);
CREATE INDEX idx_voice_conversations_user_id ON voice_conversations(user_id);
CREATE INDEX idx_voice_conversations_state ON voice_conversations(conversation_state);

-- ==========================================
-- BUSINESS INTELLIGENCE (Optional Validation)
-- ==========================================

CREATE TABLE business_validations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID REFERENCES voice_conversations(id) ON DELETE CASCADE,
    business_idea TEXT NOT NULL,
    market_analysis JSONB,
    competitor_research JSONB,
    business_model_validation JSONB,
    strategy_recommendations JSONB,
    validation_score DECIMAL(3,2), -- 0.00 to 10.00
    validation_status VARCHAR(50) DEFAULT 'pending', -- 'pending', 'completed', 'failed'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Business validation indexes
CREATE INDEX idx_business_validations_conversation_id ON business_validations(conversation_id);
CREATE INDEX idx_business_validations_score ON business_validations(validation_score);
CREATE INDEX idx_business_validations_status ON business_validations(validation_status);

-- ==========================================
-- PROJECTS (Connect All Layers)
-- ==========================================

CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_name VARCHAR(255) NOT NULL,
    description TEXT,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    conversation_session_id UUID REFERENCES voice_conversations(id),
    business_validation_id UUID REFERENCES business_validations(id),
    founder_ai_agreement JSONB NOT NULL,
    technology_stack JSONB DEFAULT '["FastAPI", "React", "PostgreSQL"]',
    github_repo_url VARCHAR(500),
    github_repo_name VARCHAR(255),
    deployment_url VARCHAR(500),
    smart_contract_address VARCHAR(255),
    status VARCHAR(50) DEFAULT 'planning', -- 'planning', 'building', 'debugging', 'deployed', 'archived'
    visibility VARCHAR(20) DEFAULT 'private', -- 'private', 'public'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Project indexes
CREATE INDEX idx_projects_user_id ON projects(user_id);
CREATE INDEX idx_projects_status ON projects(status);
CREATE INDEX idx_projects_created_at ON projects(created_at);
CREATE INDEX idx_projects_github_repo ON projects(github_repo_url);

-- ==========================================
-- DREAM SESSIONS (Layer 1 - Build)
-- ==========================================

CREATE TABLE dream_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    build_request TEXT NOT NULL,
    strategic_analysis JSONB,
    generated_files JSONB,
    generation_quality_score DECIMAL(3,2),
    file_count INTEGER DEFAULT 0,
    total_lines_generated INTEGER DEFAULT 0,
    generation_time_seconds DECIMAL(8,2),
    llm_provider VARCHAR(50),
    status VARCHAR(50) DEFAULT 'completed', -- 'pending', 'generating', 'completed', 'failed'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Dream session indexes
CREATE INDEX idx_dream_sessions_project_id ON dream_sessions(project_id);
CREATE INDEX idx_dream_sessions_status ON dream_sessions(status);
CREATE INDEX idx_dream_sessions_quality_score ON dream_sessions(generation_quality_score);

-- ==========================================
-- DEBUG SESSIONS (Layer 2 - Debug with Monaco)
-- ==========================================

CREATE TABLE debug_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    session_name VARCHAR(255),
    monaco_workspace_state JSONB,
    collaboration_users JSONB DEFAULT '[]',
    github_sync_history JSONB DEFAULT '[]',
    ai_interactions JSONB DEFAULT '[]',
    debug_questions_count INTEGER DEFAULT 0,
    code_changes_count INTEGER DEFAULT 0,
    test_runs_count INTEGER DEFAULT 0,
    status VARCHAR(50) DEFAULT 'active', -- 'active', 'paused', 'completed', 'archived'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Debug session indexes
CREATE INDEX idx_debug_sessions_project_id ON debug_sessions(project_id);
CREATE INDEX idx_debug_sessions_status ON debug_sessions(status);

-- ==========================================
-- CONTRACT METHOD COMPLIANCE (Patent-worthy)
-- ==========================================

CREATE TABLE contract_compliance (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    founder_contract JSONB NOT NULL,
    compliance_monitoring JSONB DEFAULT '[]',
    deviation_alerts JSONB DEFAULT '[]',
    compliance_score DECIMAL(3,2), -- 0.00 to 10.00
    last_compliance_check TIMESTAMP WITH TIME ZONE,
    total_violations INTEGER DEFAULT 0,
    auto_corrections_applied INTEGER DEFAULT 0,
    status VARCHAR(50) DEFAULT 'active', -- 'active', 'violated', 'corrected'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Contract compliance indexes
CREATE INDEX idx_contract_compliance_project_id ON contract_compliance(project_id);
CREATE INDEX idx_contract_compliance_score ON contract_compliance(compliance_score);
CREATE INDEX idx_contract_compliance_status ON contract_compliance(status);

-- ==========================================
-- SMART CONTRACT REVENUE (Patent-worthy)
-- ==========================================

CREATE TABLE revenue_sharing (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    smart_contract_address VARCHAR(255),
    blockchain_network VARCHAR(50) DEFAULT 'ethereum',
    revenue_tracked DECIMAL(15,2) DEFAULT 0.00,
    platform_share DECIMAL(15,2) DEFAULT 0.00,
    founder_share DECIMAL(15,2) DEFAULT 0.00,
    total_transactions INTEGER DEFAULT 0,
    digital_fingerprint VARCHAR(500),
    watermark_embedded BOOLEAN DEFAULT FALSE,
    last_revenue_sync TIMESTAMP WITH TIME ZONE,
    status VARCHAR(50) DEFAULT 'active', -- 'active', 'paused', 'completed'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Revenue sharing indexes
CREATE INDEX idx_revenue_sharing_project_id ON revenue_sharing(project_id);
CREATE INDEX idx_revenue_sharing_contract_address ON revenue_sharing(smart_contract_address);
CREATE INDEX idx_revenue_sharing_revenue ON revenue_sharing(revenue_tracked);

-- ==========================================
-- GITHUB INTEGRATION TRACKING
-- ==========================================

CREATE TABLE github_integrations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    repository_url VARCHAR(500) NOT NULL,
    repository_name VARCHAR(255),
    default_branch VARCHAR(100) DEFAULT 'main',
    last_sync_commit VARCHAR(255),
    sync_frequency VARCHAR(50) DEFAULT 'manual', -- 'manual', 'auto', 'realtime'
    total_pushes INTEGER DEFAULT 0,
    total_pulls INTEGER DEFAULT 0,
    last_push_at TIMESTAMP WITH TIME ZONE,
    last_pull_at TIMESTAMP WITH TIME ZONE,
    sync_status VARCHAR(50) DEFAULT 'connected', -- 'connected', 'error', 'disconnected'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- GitHub integration indexes
CREATE INDEX idx_github_integrations_project_id ON github_integrations(project_id);
CREATE INDEX idx_github_integrations_repo_url ON github_integrations(repository_url);
CREATE INDEX idx_github_integrations_sync_status ON github_integrations(sync_status);

-- ==========================================
-- API USAGE TRACKING
-- ==========================================

CREATE TABLE api_usage (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    endpoint VARCHAR(255) NOT NULL,
    method VARCHAR(10) NOT NULL,
    status_code INTEGER,
    response_time_ms DECIMAL(8,2),
    llm_provider VARCHAR(50),
    tokens_used INTEGER DEFAULT 0,
    cost_usd DECIMAL(10,4) DEFAULT 0.0000,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- API usage indexes
CREATE INDEX idx_api_usage_user_id ON api_usage(user_id);
CREATE INDEX idx_api_usage_endpoint ON api_usage(endpoint);
CREATE INDEX idx_api_usage_created_at ON api_usage(created_at);
CREATE INDEX idx_api_usage_llm_provider ON api_usage(llm_provider);

-- ==========================================
-- SYSTEM AUDIT LOG
-- ==========================================

CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(255) NOT NULL,
    resource_type VARCHAR(100),
    resource_id UUID,
    old_values JSONB,
    new_values JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Audit log indexes
CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_action ON audit_logs(action);
CREATE INDEX idx_audit_logs_resource_type ON audit_logs(resource_type);
CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at);

-- ==========================================
-- TRIGGERS FOR UPDATED_AT
-- ==========================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply updated_at triggers to relevant tables
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_voice_conversations_updated_at BEFORE UPDATE ON voice_conversations FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_business_validations_updated_at BEFORE UPDATE ON business_validations FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_projects_updated_at BEFORE UPDATE ON projects FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_dream_sessions_updated_at BEFORE UPDATE ON dream_sessions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_debug_sessions_updated_at BEFORE UPDATE ON debug_sessions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_contract_compliance_updated_at BEFORE UPDATE ON contract_compliance FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_revenue_sharing_updated_at BEFORE UPDATE ON revenue_sharing FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_github_integrations_updated_at BEFORE UPDATE ON github_integrations FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ==========================================
-- INITIAL DATA SETUP
-- ==========================================

-- Create default admin user (password: 'admin123' - change in production!)
INSERT INTO users (email, hashed_password, full_name, founder_type, is_active, is_verified) 
VALUES (
    'admin@aidebugger.factory',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewHgM2.nS3h8QjHq', -- admin123
    'AI Debugger Factory Admin',
    'technical',
    TRUE,
    TRUE
);

-- ==========================================
-- VIEWS FOR ANALYTICS
-- ==========================================

-- Project analytics view
CREATE OR REPLACE VIEW project_analytics AS
SELECT 
    p.id,
    p.project_name,
    p.status,
    p.created_at,
    u.email as owner_email,
    u.founder_type,
    COALESCE(ds.generation_count, 0) as total_generations,
    COALESCE(dbs.debug_count, 0) as total_debug_sessions,
    COALESCE(rs.revenue_tracked, 0) as total_revenue
FROM projects p
JOIN users u ON p.user_id = u.id
LEFT JOIN (
    SELECT project_id, COUNT(*) as generation_count 
    FROM dream_sessions 
    GROUP BY project_id
) ds ON p.id = ds.project_id
LEFT JOIN (
    SELECT project_id, COUNT(*) as debug_count 
    FROM debug_sessions 
    GROUP BY project_id
) dbs ON p.id = dbs.project_id
LEFT JOIN (
    SELECT project_id, SUM(revenue_tracked) as revenue_tracked 
    FROM revenue_sharing 
    GROUP BY project_id
) rs ON p.id = rs.project_id;

-- User analytics view
CREATE OR REPLACE VIEW user_analytics AS
SELECT 
    u.id,
    u.email,
    u.founder_type,
    u.created_at,
    COUNT(p.id) as total_projects,
    COUNT(vc.id) as total_conversations,
    COALESCE(SUM(rs.platform_share), 0) as total_platform_revenue,
    COALESCE(SUM(rs.founder_share), 0) as total_founder_revenue
FROM users u
LEFT JOIN projects p ON u.id = p.user_id
LEFT JOIN voice_conversations vc ON u.id = vc.user_id
LEFT JOIN revenue_sharing rs ON p.id = rs.project_id
GROUP BY u.id, u.email, u.founder_type, u.created_at;

COMMENT ON DATABASE dreamengine_db IS 'AI Debugger Factory - Revolutionary AI-powered development platform with patent-worthy innovations';
export type Category = "attendance" | "re_evaluation" | "re_registration" | "medical_leave" | "grade_grievance";
export type RunStatus = "pending" | "running" | "completed" | "escalated" | "failed";

export interface PetitionPayload { category: Category; description: string; attendance_percentage?: number; prescribed_minimum?: number; medical_documented?: boolean; condonation_requested?: boolean; student_reference?: string; }
export interface SubmitResponse { run_id: string; status: RunStatus; correlation_id: string; duplicate: boolean; }
export interface RunStatusResponse { run_id: string; status: RunStatus; correlation_id: string; created_at: number; updated_at: number; }
export interface Citation { source_id: string; document: string; page: number; clause: string; passage: string; }
export interface TriageResult { advisory_notice: string; petition_facts: Record<string, unknown>; base_provision?: Citation | null; modifying_provision?: Citation | null; missing_information: string[]; conflicts: string[]; proposed_eligibility: string; routing: string; human_review_required: boolean; verification: string; citations: Citation[]; prompt_version: string; }

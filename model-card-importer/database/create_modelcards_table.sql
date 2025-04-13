-- SQL Server script to create the ModelCards table

-- Drop the table if it already exists (optional, use with caution)
-- IF OBJECT_ID('dbo.ModelCards', 'U') IS NOT NULL
-- DROP TABLE dbo.ModelCards;
-- GO

CREATE TABLE dbo.ModelCards (
    ModelCardID INT IDENTITY(1,1) PRIMARY KEY,

    -- Basic Information Fields
    [name] NVARCHAR(255) NULL,
    [description] NVARCHAR(MAX) NULL,
    modelStage NVARCHAR(255) NULL,
    [type] NVARCHAR(255) NULL,
    modelCategory NVARCHAR(255) NULL,
    modelUseCategory NVARCHAR(255) NULL,
    modelOrganization NVARCHAR(255) NULL,
    modelRisk NVARCHAR(255) NULL,
    custom_mocApplicationFormId NVARCHAR(255) NULL, -- Renamed: custom.mocApplicationFormId

    -- Overview Fields (Renamed: dots/spaces replaced with underscores)
    custom_Overview_Name_of_the_AI_Solution NVARCHAR(500) NULL,
    custom_Overview_Describe_the_AI_solution NVARCHAR(MAX) NULL,
    custom_Overview_How_is_the_AI_solution_budgeted NVARCHAR(MAX) NULL,
    custom_Overview_Describe_the_business_value_for_MDA_using_the_AI_solution NVARCHAR(MAX) NULL,
    custom_Overview_List_any_business_metrics_or_KPIs_that_will_be_used_to_ascertain_the_business_value NVARCHAR(MAX) NULL,
    custom_Overview_Which_MDA_Strategic_goal_is_supported_by_the_AI_Solution NVARCHAR(MAX) NULL,
    custom_Overview_Describe_how_the_technology_fits_into_MDACC_strategy NVARCHAR(MAX) NULL,
    custom_Overview_Funding_source_of_the_technical_implementation NVARCHAR(500) NULL,
    custom_Overview_Reimbursement_status_if_applicable NVARCHAR(255) NULL,
    custom_Overview_The_current_Stage_in_the_lifecycle_of_the_AI_system NVARCHAR(255) NULL,
    custom_Overview_If_in_production_the_date_that_the_AI_system_was_deployed_for_production_usage NVARCHAR(255) NULL, -- Consider DATE/DATETIME2
    custom_Overview_If_in_production_the_current_version_used_in_production NVARCHAR(255) NULL,
    custom_Overview_Impact_to_the_business NVARCHAR(MAX) NULL,
    custom_Overview_Final_clinical_risk_level_identified_for_the_AI_Solution NVARCHAR(255) NULL,
    custom_Overview_Is_it_model_available_globally NVARCHAR(50) NULL, -- Consider BIT
    custom_Overview_Transparency_Intelligibility_and_Accountability_mechanisms_if_applicable NVARCHAR(MAX) NULL,
    custom_Overview_3rd_Party_Information_if_Applicable NVARCHAR(MAX) NULL,
    custom_Overview_Evaluation_References_if_Available NVARCHAR(MAX) NULL,
    custom_Overview_Peer_Reviewed_Publications NVARCHAR(MAX) NULL,
    custom_Overview_Stakeholders_consulted_during_design_of_intervention NVARCHAR(MAX) NULL,
    custom_Overview_Patient_consent_or_disclosure_required_or_suggested NVARCHAR(255) NULL, -- Consider BIT
    custom_Overview_Clinical_Trial_if_Available NVARCHAR(500) NULL,
    custom_Overview_Model_ID NVARCHAR(255) NULL,

    -- Accountability Fields (Renamed)
    custom_Accountability_Who_is_the_business_sponsor NVARCHAR(255) NULL,
    custom_Accountability_What_organization_does_the_business_sponsor_belong_to NVARCHAR(255) NULL,
    custom_Accountability_Who_is_the_technical_contact_for_the_business_sponsor NVARCHAR(255) NULL,
    custom_Accountability_Owner_Developer_of_the_AI_Solution NVARCHAR(255) NULL,
    custom_Accountability_Accountable_AI_governance_officer_for_the_AI_Solution NVARCHAR(255) NULL,
    custom_Accountability_Accountable_legal_officer_for_the_AI_solution NVARCHAR(255) NULL,
    custom_Accountability_Responsible_for_completing_and_or_signing_off_on_the_independent_review_of_the_AI_Solution NVARCHAR(255) NULL,

    -- Scope, Usages, Limitations Fields (Renamed & Shortened)
    custom_Scope_Usage_Clinical_Research_Ops NVARCHAR(255) NULL,
    custom_Scope_Usage_User_Description NVARCHAR(MAX) NULL, -- Shortened
    custom_Scope_Usage_Intended_Use NVARCHAR(MAX) NULL,
    custom_Scope_Usage_Intended_Patient_Pop NVARCHAR(MAX) NULL,
    custom_Scope_Usage_OutOfScope_Settings NVARCHAR(MAX) NULL,
    custom_Scope_Usages_Limitations_Known_risks_and_limitations NVARCHAR(MAX) NULL,
    custom_Scope_Usages_Limitations_Known_biases_or_ethical_considerations_Are_certain_target_groups_unrepresented NVARCHAR(MAX) NULL,
    custom_Scope_Usages_Limitations_What_is_the_approach_to_mitigate_any_potential_biases NVARCHAR(MAX) NULL,
    custom_Scope_Usages_Limitations_Describe_the_outcomes_and_outputs_of_the_model NVARCHAR(MAX) NULL,

    -- Solution Details Fields (Renamed)
    custom_Solution_Details_Build_Buy_Partner NVARCHAR(255) NULL,
    custom_Solution_Details_Used_In_Clinical_Mgmt NVARCHAR(50) NULL, -- Consider BIT
    custom_Solution_Details_Patient_Consent_Disclosure NVARCHAR(50) NULL, -- Consider BIT
    custom_Solution_Details_HCP_Responsible_For_Decision NVARCHAR(50) NULL, -- Shortened & Consider BIT
    custom_Solution_Details_Workflow_Changes NVARCHAR(50) NULL, -- Consider BIT
    custom_Solution_Details_Transition_Training_Plan NVARCHAR(50) NULL, -- Consider BIT
    custom_Solution_Details_Automates_Decisions NVARCHAR(50) NULL, -- Consider BIT
    custom_Solution_Details_Error_Detection NVARCHAR(MAX) NULL,

    -- Data Fields (Renamed & Shortened)
    custom_Data_Sensitivity_Classification NVARCHAR(255) NULL, -- Shortened
    custom_Data_Access_Patient_Info NVARCHAR(50) NULL, -- Consider BIT
    custom_Data_Patient_Data_Available_To_Vendor NVARCHAR(50) NULL, -- Consider BIT
    custom_Data_Patient_Data_Storage_Location NVARCHAR(500) NULL,
    custom_Data_What_data_is_needed_for_the_model_to_function NVARCHAR(MAX) NULL,
    custom_Data_What_data_is_stored_and_where NVARCHAR(MAX) NULL,
    custom_Data_Who_has_access_to_this_data NVARCHAR(MAX) NULL,
    custom_Data_Who_maintains_the_data NVARCHAR(255) NULL,
    custom_Data_How_long_is_data_maintained NVARCHAR(255) NULL,
    custom_Data_Can_data_be_edited_If_so_is_an_audit_trail_available NVARCHAR(50) NULL, -- Consider BIT
    custom_Data_Do_we_have_high_quality_data_accessible_for_the_AI_Solution NVARCHAR(50) NULL, -- Consider BIT
    custom_Data_Output_Input_data_type NVARCHAR(255) NULL,
    custom_Data_Development_data_characterization NVARCHAR(MAX) NULL,

    -- Implementation and Policy Adherence Fields (Renamed)
    custom_Implementation_and_Policy_Adherence_Describe_the_technology_briefly NVARCHAR(MAX) NULL,
    custom_Implementation_and_Policy_Adherence_Does_the_technology_use_LLMs_What_foundation_model_is_used NVARCHAR(500) NULL,
    custom_Implementation_and_Policy_Adherence_Methodology_used_to_implement_the_AI_Solution NVARCHAR(500) NULL,
    custom_Implementation_and_Policy_Adherence_Describe_how_the_technology_handles_errors_Include_any_mitigation_strategies NVARCHAR(MAX) NULL,
    custom_Implementation_and_Policy_Adherence_Does_the_technology_have_a_means_to_report_or_identify_adverse_events NVARCHAR(50) NULL, -- Consider BIT
    custom_Implementation_and_Policy_Adherence_Has_the_technology_been_validated_by_the_vendor NVARCHAR(50) NULL, -- Consider BIT
    custom_Implementation_and_Policy_Adherence_Is_the_technology_cloud_based_or_hosted_locally NVARCHAR(50) NULL,
    custom_Implementation_and_Policy_Adherence_If_cloud_based_is_the_vendor_TX_RAMP_compliant NVARCHAR(50) NULL, -- Consider BIT
    custom_Implementation_and_Policy_Adherence_If_cloud_based_who_has_access_to_the_MDA_data NVARCHAR(255) NULL,
    custom_Implementation_and_Policy_Adherence_Does_the_vendor_have_a_Business_Associates_agreement_with_MDA NVARCHAR(50) NULL, -- Consider BIT
    custom_Implementation_and_Policy_Adherence_Is_the_AI_Solution_compliant_with_MDACC_policies_and_applicable_regulations NVARCHAR(MAX) NULL,
    custom_Implementation_and_Policy_Adherence_Does_the_technology_meet_all_State_of_Texas_regulations_and_laws NVARCHAR(50) NULL, -- Consider BIT
    custom_Implementation_and_Policy_Adherence_Does_the_technology_meet_all_Federal_regulations NVARCHAR(50) NULL, -- Consider BIT
    custom_Impl_Policy_Practitioner_Risk NVARCHAR(50) NULL, -- Shortened
    custom_Impl_Policy_Records_Patients_Employees NVARCHAR(50) NULL, -- Shortened
    custom_Impl_Policy_Recording_Access_Purpose_Duration NVARCHAR(MAX) NULL, -- Shortened
    custom_Impl_Policy_Recording_Consent_Obtainable NVARCHAR(50) NULL, -- Shortened
    custom_Impl_Policy_Needs_MDA_Training NVARCHAR(50) NULL, -- Shortened
    custom_Impl_Policy_MDA_Training_Vendor_IP_Rights NVARCHAR(50) NULL, -- Shortened
    custom_Impl_Policy_Secondary_Use_Wording NVARCHAR(50) NULL, -- Shortened
    custom_Impl_Policy_BAA_Needed NVARCHAR(50) NULL, -- Shortened
    custom_Impl_Policy_Vendor_Retrains_Model NVARCHAR(50) NULL, -- Shortened
    custom_Impl_Policy_Vendor_Retrain_Data NVARCHAR(MAX) NULL, -- Shortened
    custom_Impl_Policy_Validation_Reference NVARCHAR(MAX) NULL, -- Shortened

    -- Monitoring and Maintenance Fields (Renamed & Shortened)
    custom_Monitor_Maint_Performance_Assessment NVARCHAR(MAX) NULL,
    custom_Monitor_Maint_Metric_Used NVARCHAR(255) NULL,
    custom_Monitor_Maint_Target NVARCHAR(255) NULL,
    custom_Monitor_Maint_Drift_Identification NVARCHAR(MAX) NULL,
    custom_Monitor_Maint_Updates_Validation NVARCHAR(MAX) NULL,
    custom_Monitor_Maint_Maintenance_Plan NVARCHAR(MAX) NULL,
    custom_Monitor_Maint_Update_Frequency NVARCHAR(255) NULL,
    custom_Monitor_Maint_MDA_FineTune_Testing NVARCHAR(MAX) NULL,
    custom_Monitor_Maint_Security_Review_Approver NVARCHAR(255) NULL,

    -- Key Metrics - Usefulness, Usability, and Efficacy Fields (Renamed & Shortened)
    custom_Metrics_Usefulness_Goal NVARCHAR(MAX) NULL,
    custom_Metrics_Usefulness_Result NVARCHAR(MAX) NULL,
    custom_Metrics_Usefulness_Interpretation NVARCHAR(MAX) NULL,
    custom_Metrics_Usefulness_Test_Type NVARCHAR(255) NULL,
    custom_Metrics_Usefulness_Testing_Data_Desc NVARCHAR(MAX) NULL,
    custom_Metrics_Usefulness_Validation_Justification NVARCHAR(MAX) NULL,

    -- Key Metrics - Fairness and Equity Fields (Renamed & Shortened)
    custom_Metrics_Fairness_Goal NVARCHAR(MAX) NULL,
    custom_Metrics_Fairness_Result NVARCHAR(MAX) NULL,
    custom_Metrics_Fairness_Interpretation NVARCHAR(MAX) NULL,
    custom_Metrics_Fairness_Test_Type NVARCHAR(255) NULL,
    custom_Metrics_Fairness_Testing_Data_Desc NVARCHAR(MAX) NULL,
    custom_Metrics_Fairness_Validation_Justification NVARCHAR(MAX) NULL,

    -- Key Metrics - Safety and Reliability Fields (Renamed & Shortened)
    custom_Metrics_Safety_Goal NVARCHAR(MAX) NULL,
    custom_Metrics_Safety_Result NVARCHAR(MAX) NULL,
    custom_Metrics_Safety_Interpretation NVARCHAR(MAX) NULL,
    custom_Metrics_Safety_Test_Type NVARCHAR(255) NULL,
    custom_Metrics_Safety_Testing_Data_Desc NVARCHAR(MAX) NULL,
    custom_Metrics_Safety_Validation_Justification NVARCHAR(MAX) NULL,

    -- Timestamps
    CreatedAt DATETIME2 DEFAULT GETDATE(),
    UpdatedAt DATETIME2 DEFAULT GETDATE()
);
GO

-- Optional: Add a trigger to update UpdatedAt on row update
-- CREATE TRIGGER TRG_ModelCards_UpdateTimestamp
-- ON dbo.ModelCards
-- AFTER UPDATE
-- AS
-- BEGIN
--     IF NOT UPDATE(UpdatedAt) -- Avoid recursive trigger calls if UpdatedAt is explicitly set
--     BEGIN
--         UPDATE dbo.ModelCards
--         SET UpdatedAt = GETDATE()
--         FROM inserted
--         WHERE dbo.ModelCards.ModelCardID = inserted.ModelCardID;
--     END
-- END;
-- GO

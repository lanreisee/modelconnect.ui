import os
import logging
import shutil
import pyodbc # Import pyodbc
from fastapi import FastAPI, File, UploadFile, HTTPException, status, Body
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any, Optional, List

# Use relative import since parser.py and db_connection.py are in the same directory
from .parser import parse_spreadsheet
from .db_connection import get_db_connection # Import DB connection function

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Configuration
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), '..', 'temp_uploads')
ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls'}

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = FastAPI(title="Model Card Importer API")

# Configure CORS
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Field Mapping (Frontend ID/JSON Key -> DB Column Name) ---
# This mapping is crucial because DB columns were shortened/renamed
FIELD_TO_COLUMN_MAP = {
    "name": "[name]", # Use brackets for reserved keywords
    "description": "[description]",
    "modelStage": "modelStage",
    "type": "[type]", # Use brackets for reserved keywords
    "modelCategory": "modelCategory",
    "modelUseCategory": "modelUseCategory",
    "modelOrganization": "modelOrganization",
    "modelRisk": "modelRisk",
    "custom.mocApplicationFormId": "custom_mocApplicationFormId",
    "custom.Overview.Name of the AI Solution": "custom_Overview_Name_of_the_AI_Solution",
    "custom.Overview.Describe the AI solution": "custom_Overview_Describe_the_AI_solution",
    "custom.Overview.How is the AI solution budgeted?": "custom_Overview_How_is_the_AI_solution_budgeted",
    "custom.Overview.Describe the business value for MDA using the AI solution": "custom_Overview_Describe_the_business_value_for_MDA_using_the_AI_solution",
    "custom.Overview.List any business metrics or KPIs that will be used to ascertain the business value": "custom_Overview_List_any_business_metrics_or_KPIs_that_will_be_used_to_ascertain_the_business_value",
    "custom.Overview.Which MDA Strategic goal is supported by the AI Solution?": "custom_Overview_Which_MDA_Strategic_goal_is_supported_by_the_AI_Solution",
    "custom.Overview.Describe how the technology fits into MDACC strategy": "custom_Overview_Describe_how_the_technology_fits_into_MDACC_strategy",
    "custom.Overview.Funding source of the technical implementation": "custom_Overview_Funding_source_of_the_technical_implementation",
    "custom.Overview.Reimbursement status, if applicable": "custom_Overview_Reimbursement_status_if_applicable",
    "custom.Overview.The current Stage in the lifecycle of the AI system": "custom_Overview_The_current_Stage_in_the_lifecycle_of_the_AI_system",
    "custom.Overview.If in production, the date that the AI system was deployed for production usage": "custom_Overview_If_in_production_the_date_that_the_AI_system_was_deployed_for_production_usage",
    "custom.Overview.If in production, the current version used in production": "custom_Overview_If_in_production_the_current_version_used_in_production",
    "custom.Overview.Impact to the business": "custom_Overview_Impact_to_the_business",
    "custom.Overview.Final clinical risk level identified for the AI Solution": "custom_Overview_Final_clinical_risk_level_identified_for_the_AI_Solution",
    "custom.Overview.Is it model available globally?": "custom_Overview_Is_it_model_available_globally",
    "custom.Overview.Transparency, Intelligibility, and Accountability mechanisms, if applicable": "custom_Overview_Transparency_Intelligibility_and_Accountability_mechanisms_if_applicable",
    "custom.Overview.3rd Party Information, if Applicable": "custom_Overview_3rd_Party_Information_if_Applicable",
    "custom.Overview.Evaluation References, if Available": "custom_Overview_Evaluation_References_if_Available",
    "custom.Overview.Peer Reviewed Publications": "custom_Overview_Peer_Reviewed_Publications",
    "custom.Overview.Stakeholders consulted during design of intervention": "custom_Overview_Stakeholders_consulted_during_design_of_intervention",
    "custom.Overview.Patient consent or disclosure required or suggested?": "custom_Overview_Patient_consent_or_disclosure_required_or_suggested",
    "custom.Overview.Clinical Trial, if Available": "custom_Overview_Clinical_Trial_if_Available",
    "custom.Overview.Model ID": "custom_Overview_Model_ID",
    "custom.Accountability.Who is the business sponsor?": "custom_Accountability_Who_is_the_business_sponsor",
    "custom.Accountability.What organization does the business sponsor belong to?": "custom_Accountability_What_organization_does_the_business_sponsor_belong_to",
    "custom.Accountability.Who is the technical contact for the business sponsor?": "custom_Accountability_Who_is_the_technical_contact_for_the_business_sponsor",
    "custom.Accountability.Owner/Developer of the AI Solution": "custom_Accountability_Owner_Developer_of_the_AI_Solution",
    "custom.Accountability.Accountable AI governance officer for the AI Solution": "custom_Accountability_Accountable_AI_governance_officer_for_the_AI_Solution",
    "custom.Accountability.Accountable legal officer for the AI solution": "custom_Accountability_Accountable_legal_officer_for_the_AI_solution",
    "custom.Accountability.Responsible for completing and/or signing-off on the independent review of the AI Solution": "custom_Accountability_Responsible_for_completing_and_or_signing_off_on_the_independent_review_of_the_AI_Solution",
    "custom.Scope, Usages, Limitations.Will the AI Solution be used in a clinical, research, or operations setting?": "custom_Scope_Usage_Clinical_Research_Ops", # Shortened
    "custom.Scope, Usages, Limitations.Describe who will use the AI tool, i.e. is the AI Solution developed for internal or external users?": "custom_Scope_Usage_User_Description", # Shortened
    "custom.Scope, Usages, Limitations.Describe how the AI tool is intended to be used": "custom_Scope_Usage_Intended_Use",
    "custom.Scope, Usages, Limitations.Who is the intended patient population?": "custom_Scope_Usage_Intended_Patient_Pop",
    "custom.Scope, Usages, Limitations.Cautioned out-of-scope settings and AI Solutions": "custom_Scope_Usage_OutOfScope_Settings",
    "custom.Scope, Usages, Limitations.Known risks and limitations": "custom_Scope_Usages_Limitations_Known_risks_and_limitations",
    "custom.Scope, Usages, Limitations.Known biases or ethical considerations. Are certain target groups unrepresented?": "custom_Scope_Usages_Limitations_Known_biases_or_ethical_considerations_Are_certain_target_groups_unrepresented",
    "custom.Scope, Usages, Limitations.What is the approach to mitigate any potential biases?": "custom_Scope_Usages_Limitations_What_is_the_approach_to_mitigate_any_potential_biases",
    "custom.Scope, Usages, Limitations.Describe the outcomes and outputs of the model": "custom_Scope_Usages_Limitations_Describe_the_outcomes_and_outputs_of_the_model",
    "custom.Solution Details.Is the AI Solution a build: internal, buy, or partner:co-development?": "custom_Solution_Details_Build_Buy_Partner",
    "custom.Solution Details.If in a clinical setting, will the solution be used in the clinical management of patients?": "custom_Solution_Details_Used_In_Clinical_Mgmt",
    "custom.Solution Details.Patient consent or disclosure required or suggested?": "custom_Solution_Details_Patient_Consent_Disclosure",
    "custom.Solution Details.If in a clinical setting, will a certified health care provider be responsible for any AI assisted decision?": "custom_Solution_Details_HCP_Responsible_For_Decision", # Shortened
    "custom.Solution Details.Will there be any significant changes to workflow after deployment of the AI solution?": "custom_Solution_Details_Workflow_Changes",
    "custom.Solution Details.If there is a workflow impact, will there be a transition and training plan?": "custom_Solution_Details_Transition_Training_Plan",
    "custom.Solution Details.Does the AI Solution automate any decisions-clinical or other?": "custom_Solution_Details_Automates_Decisions",
    "custom.Solution Details.If so, how are errors and poor performance detected?": "custom_Solution_Details_Error_Detection",
    "custom.Data.Data sensitivity classification, e.g. public, internal, confidential, restricted confidential for data used in the model during training and/or execution": "custom_Data_Sensitivity_Classification", # Shortened
    "custom.Data.Does the AI Solution have access to patient specific information?": "custom_Data_Access_Patient_Info",
    "custom.Data.If the solution has access to patient data, is the information available to the vendor?": "custom_Data_Patient_Data_Available_To_Vendor",
    "custom.Data.If the solution has access to patient data, where is the information stored?": "custom_Data_Patient_Data_Storage_Location",
    "custom.Data.What data is needed for the model to function?": "custom_Data_What_data_is_needed_for_the_model_to_function",
    "custom.Data.What data is stored and where?": "custom_Data_What_data_is_stored_and_where",
    "custom.Data.Who has access to this data?": "custom_Data_Who_has_access_to_this_data",
    "custom.Data.Who maintains the data?": "custom_Data_Who_maintains_the_data",
    "custom.Data.How long is data maintained?": "custom_Data_How_long_is_data_maintained",
    "custom.Data.Can data be edited? If so, is an audit trail available?": "custom_Data_Can_data_be_edited_If_so_is_an_audit_trail_available",
    "custom.Data.Do we have high quality data accessible for the AI Solution?": "custom_Data_Do_we_have_high_quality_data_accessible_for_the_AI_Solution",
    "custom.Data.Output/Input data type": "custom_Data_Output_Input_data_type",
    "custom.Data.Development data characterization": "custom_Data_Development_data_characterization",
    "custom.Implementation and Policy Adherence.Describe the technology briefly": "custom_Implementation_and_Policy_Adherence_Describe_the_technology_briefly",
    "custom.Implementation and Policy Adherence.Does the technology use LLMs? What foundation model is used?": "custom_Implementation_and_Policy_Adherence_Does_the_technology_use_LLMs_What_foundation_model_is_used",
    "custom.Implementation and Policy Adherence.Methodology used to implement the AI Solution": "custom_Implementation_and_Policy_Adherence_Methodology_used_to_implement_the_AI_Solution",
    "custom.Implementation and Policy Adherence.Describe how the technology handles errors? Include any mitigation strategies.": "custom_Implementation_and_Policy_Adherence_Describe_how_the_technology_handles_errors_Include_any_mitigation_strategies",
    "custom.Implementation and Policy Adherence.Does the technology have a means to report or identify adverse events?": "custom_Implementation_and_Policy_Adherence_Does_the_technology_have_a_means_to_report_or_identify_adverse_events",
    "custom.Implementation and Policy Adherence.Has the technology been validated by the vendor?": "custom_Implementation_and_Policy_Adherence_Has_the_technology_been_validated_by_the_vendor",
    "custom.Implementation and Policy Adherence.Is the technology cloud based or hosted locally?": "custom_Implementation_and_Policy_Adherence_Is_the_technology_cloud_based_or_hosted_locally",
    "custom.Implementation and Policy Adherence.If cloud based, is the vendor TX-RAMP compliant?": "custom_Implementation_and_Policy_Adherence_If_cloud_based_is_the_vendor_TX_RAMP_compliant",
    "custom.Implementation and Policy Adherence.If cloud based, who has access to the MDA data?": "custom_Implementation_and_Policy_Adherence_If_cloud_based_who_has_access_to_the_MDA_data",
    "custom.Implementation and Policy Adherence.Does the vendor have a Business Associates agreement with MDA?": "custom_Implementation_and_Policy_Adherence_Does_the_vendor_have_a_Business_Associates_agreement_with_MDA",
    "custom.Implementation and Policy Adherence.Is the AI Solution compliant with MDACC policies and applicable regulations": "custom_Implementation_and_Policy_Adherence_Is_the_AI_Solution_compliant_with_MDACC_policies_and_applicable_regulations",
    "custom.Implementation and Policy Adherence.Does the technology meet all State of Texas regulations and laws?": "custom_Implementation_and_Policy_Adherence_Does_the_technology_meet_all_State_of_Texas_regulations_and_laws",
    "custom.Implementation and Policy Adherence.Does the technology meet all Federal regulations?": "custom_Implementation_and_Policy_Adherence_Does_the_technology_meet_all_Federal_regulations",
    "custom.Implementation and Policy Adherence.Does the technology place practitioners / employees at greater risk?": "custom_Impl_Policy_Practitioner_Risk", # Shortened
    "custom.Implementation and Policy Adherence.Does the AI solution involve recording of patients or employees?": "custom_Impl_Policy_Records_Patients_Employees", # Shortened
    "custom.Implementation and Policy Adherence.If recording is present, who has access to the recordings, for what purposes, and for how long?": "custom_Impl_Policy_Recording_Access_Purpose_Duration", # Shortened
    "custom.Implementation and Policy Adherence.If recording is present, is consent necessary and obtainable?": "custom_Impl_Policy_Recording_Consent_Obtainable", # Shortened
    "custom.Implementation and Policy Adherence.Does the AI Solution need to be adapted / trained for MDA specifically?": "custom_Impl_Policy_Needs_MDA_Training", # Shortened
    "custom.Implementation and Policy Adherence.If the AI solution needs to be trained for MDA, does the vendor have any intellectual property rights to the trained model?": "custom_Impl_Policy_MDA_Training_Vendor_IP_Rights", # Shortened
    "custom.Implementation and Policy Adherence.Is there explicit wording in agreement covering secondary use of MDA data?": "custom_Impl_Policy_Secondary_Use_Wording", # Shortened
    "custom.Implementation and Policy Adherence.Is a BAA needed to allow vendor to handle MDA data?": "custom_Impl_Policy_BAA_Needed", # Shortened
    "custom.Implementation and Policy Adherence.Are MDA data used by vendor to re-train their model?": "custom_Impl_Policy_Vendor_Retrains_Model", # Shortened
    "custom.Implementation and Policy Adherence.If MDA data is being used by vendor to re-train their model, which data?": "custom_Impl_Policy_Vendor_Retrain_Data", # Shortened
    "custom.Implementation and Policy Adherence.If the technology has been validated, please reference any published studies or marketing material": "custom_Impl_Policy_Validation_Reference", # Shortened
    "custom.Monitoring and Maintenance.After implementation, how will the performance of the AI solution be assessed?": "custom_Monitor_Maint_Performance_Assessment",
    "custom.Monitoring and Maintenance.What metric will be used?": "custom_Monitor_Maint_Metric_Used",
    "custom.Monitoring and Maintenance.What is the target?": "custom_Monitor_Maint_Target",
    "custom.Monitoring and Maintenance.How does the model identify drift?, e.g. drift may occur when the data which is used to train the model no longer represents the current situation": "custom_Monitor_Maint_Drift_Identification", # Shortened
    "custom.Monitoring and Maintenance.How does the model handle updates? How is it validated?": "custom_Monitor_Maint_Updates_Validation",
    "custom.Monitoring and Maintenance.How will the AI solution be maintained?": "custom_Monitor_Maint_Maintenance_Plan",
    "custom.Monitoring and Maintenance.How frequent are updates made?": "custom_Monitor_Maint_Update_Frequency",
    "custom.Monitoring and Maintenance.If there is MDA specific fine tuning of models, how is testing performed prior to deployment of updates?": "custom_Monitor_Maint_MDA_FineTune_Testing", # Shortened
    "custom.Monitoring and Maintenance.Approver Name for Security and compliance environment practice review": "custom_Monitor_Maint_Security_Review_Approver",
    "custom.Key Metrics.Usefulness, Usability, and Efficacy-Goal of metric": "custom_Metrics_Usefulness_Goal",
    "custom.Key Metrics.Usefulness, Usability, and Efficacy-Result": "custom_Metrics_Usefulness_Result",
    "custom.Key Metrics.Usefulness, Usability, and Efficacy-Interpretation": "custom_Metrics_Usefulness_Interpretation",
    "custom.Key Metrics.Usefulness, Usability, and Efficacy-Test Type": "custom_Metrics_Usefulness_Test_Type",
    "custom.Key Metrics.Usefulness, Usability, and Efficacy-Testing Data Description": "custom_Metrics_Usefulness_Testing_Data_Desc",
    "custom.Key Metrics.Usefulness, Usability, and Efficacy-Validation Process and Justification": "custom_Metrics_Usefulness_Validation_Justification",
    "custom.Key Metrics.Fairness and Equity-Goal of metric": "custom_Metrics_Fairness_Goal",
    "custom.Key Metrics.Fairness and Equity-Result": "custom_Metrics_Fairness_Result",
    "custom.Key Metrics.Fairness and Equity-Interpretation": "custom_Metrics_Fairness_Interpretation",
    "custom.Key Metrics.Fairness and Equity-Test Type": "custom_Metrics_Fairness_Test_Type",
    "custom.Key Metrics.Fairness and Equity-Testing Data Description": "custom_Metrics_Fairness_Testing_Data_Desc",
    "custom.Key Metrics.Fairness and Equity-Validation Process and Justification": "custom_Metrics_Fairness_Validation_Justification",
    "custom.Key Metrics.Safety and Reliability-Goal of metric": "custom_Metrics_Safety_Goal",
    "custom.Key Metrics.Safety and Reliability-Result": "custom_Metrics_Safety_Result",
    "custom.Key Metrics.Safety and Reliability-Interpretation": "custom_Metrics_Safety_Interpretation",
    "custom.Key Metrics.Safety and Reliability-Test Type": "custom_Metrics_Safety_Test_Type",
    "custom.Key Metrics.Safety and Reliability-Testing Data Description": "custom_Metrics_Safety_Testing_Data_Desc",
    "custom.Key Metrics.Safety and Reliability-Validation Process and Justification": "custom_Metrics_Safety_Validation_Justification",
}
# ---------------------------------------------------------


def allowed_file(filename):
    """Checks if the file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.post("/upload-for-form", response_model=Optional[List[Dict[str, Any]]])
async def upload_file_for_form(file: UploadFile = File(...)):
    """
    Handles spreadsheet upload, parses all rows, and returns data
    for form population.
    """
    # ... (rest of the upload logic remains the same) ...
    # ... (it returns the list of dicts with original keys) ...

@app.post("/save-model-card")
async def save_model_card(model_card_data: Dict[str, Any] = Body(...)):
    """
    Receives model card data (presumably from the frontend form submission)
    and saves it to the SQL Server database.
    """
    cnxn = None
    cursor = None
    try:
        cnxn = get_db_connection()
        if not cnxn:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database connection failed.")

        cursor = cnxn.cursor()

        # Prepare data for insertion: map keys and filter based on map
        db_data = {}
        for form_key, db_column in FIELD_TO_COLUMN_MAP.items():
            if form_key in model_card_data:
                 # Ensure None is inserted for empty strings from form if column allows NULL
                value = model_card_data[form_key]
                db_data[db_column] = value if value != '' else None
            # else:
                # Handle missing keys if necessary, maybe set default NULL or raise error
                # db_data[db_column] = None # Example: Set missing keys to NULL

        if not db_data:
             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No valid data received.")

        # Construct INSERT statement dynamically
        columns = ', '.join(db_data.keys())
        placeholders = ', '.join('?' * len(db_data)) # Use ? as placeholder for pyodbc
        sql = f"INSERT INTO dbo.ModelCards ({columns}) VALUES ({placeholders})"

        values = tuple(db_data.values())

        logging.info(f"Executing SQL: {sql}")
        logging.info(f"With values: {values}")

        cursor.execute(sql, values)
        cnxn.commit()

        logging.info("Successfully inserted data into ModelCards table.")
        return {"message": "Model card data saved successfully."}

    except pyodbc.Error as ex:
        sqlstate = ex.args[0]
        logging.error(f"Database error during save: {sqlstate} - {ex}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {ex}")
    except Exception as e:
        logging.error(f"Error saving model card data: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An internal error occurred: {e}")
    finally:
        if cursor:
            cursor.close()
        if cnxn:
            cnxn.close()
            logging.info("Database connection closed.")


@app.get("/")
async def root():
    """Basic route for testing if the server is running."""
    return {"message": "Model Card Importer API is running!"}

# Note: Running with uvicorn is preferred for FastAPI
# Example command: uvicorn src.app:app --reload --port 5001 --host 0.0.0.0
# The __main__ block is less common for FastAPI but can be used for simple cases
if __name__ == "__main__":
    import uvicorn
    logging.info("Starting FastAPI server with Uvicorn...")
    # Run directly for simple testing; use command line for more control
    uvicorn.run("app:app", host="127.0.0.1", port=5001, log_level="info", reload=True) # Use string format for reload

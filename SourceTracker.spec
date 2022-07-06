/*
A KBase module: SourceTracker
*/

module SourceTracker {
    typedef structure {
        string report_name;
        string report_ref;
    } ReportResults;

    typedef structure {
        string workspace_name;
        int workspace_id;
        string amplicon_matrix_ref;
        string attri_mapping_ref;
        string associated_matrix_obj_ref;
        float threshold;
        int taxonomy_level;
        mapping<string, string> grouping_label;
        string sink_or_sample;
        string meta_field;
        string associated_matrix_row;
        int ascending;
    } SourceTrackerInput;

    /*
        This example function accepts any number of parameters and returns results in a KBaseReport
    */
    funcdef run_SourceTracker(SourceTrackerInput params) returns (ReportResults output) authentication required;

};

# -*- coding: utf-8 -*-
#BEGIN_HEADER
import logging
import os
import uuid
from installed_clients.KBaseReportClient import KBaseReport
from installed_clients.DataFileUtilClient import DataFileUtil
from importlib.metadata import metadata
from itertools import accumulate
import numpy as np
import pandas as pd
from SourceTracker.utils import (_gibbs, _sourcetrackerUtil, _gibbs_defaults)

#END_HEADER


class SourceTracker:
    '''
    Module Name:
    SourceTracker

    Module Description:
    A KBase module: SourceTracker
    '''

    ######## WARNING FOR GEVENT USERS ####### noqa
    # Since asynchronous IO can lead to methods - even the same method -
    # interrupting each other, you must be *very* careful when using global
    # state. A method could easily clobber the state set by another while
    # the latter method is running.
    ######################################### noqa
    VERSION = "0.0.4"
    GIT_URL = "https://github.com/silyasm/SourceTracker"
    GIT_COMMIT_HASH = "5622ff7fb08b0f3942376d922c3e834f77d8be8a"

    #BEGIN_CLASS_HEADER
    #END_CLASS_HEADER

    # config contains contents of config file in a hash or None if it couldn't
    # be found
    def __init__(self, config):
        #BEGIN_CONSTRUCTOR
        self.callback_url = os.environ['SDK_CALLBACK_URL']
        self.token = os.environ['KB_AUTH_TOKEN']
        self.wsURL = config['workspace-url']
        self.shared_folder = config['scratch']
        logging.basicConfig(format='%(created)s %(levelname)s: %(message)s',
                            level=logging.INFO)
        #END_CONSTRUCTOR
        pass


    def run_SourceTracker(self, ctx, params):
        """
        This example function accepts any number of parameters and returns results in a KBaseReport
        :param params: instance of type "SourceTrackerInput" -> structure:
           parameter "workspace_name" of String, parameter "workspace_id" of
           Long, parameter "amplicon_matrix_ref" of String, parameter
           "attri_mapping_ref" of String, parameter "threshold" of Double,
           parameter "taxonomy_level" of Long, parameter "grouping_label" of
           mapping from String to String, parameter "sink_label" of String,
           parameter "sample_type" of String, parameter "source_label" of
           String, parameter "ascending" of Long
        :returns: instance of type "ReportResults" -> structure: parameter
           "report_name" of String, parameter "report_ref" of String
        """
        # ctx is the context object
        # return variables are: output
        #BEGIN run_SourceTracker

        logging.info('start run_SourceTracker with:\n{}'.format(params))
        self.dfu = DataFileUtil(self.callback_url)

        # extract params
        # do some transformations against narrative ui

        amplicon_matrix_ref = params['amplicon_matrix_ref']
        sample_type = params['sample_type']
        cutoff = params.get('threshold', 0.005)
        grouping_label = params.get('sink_label')
        source_label = params.get('source_label')
        ascending = params.get('ascending', 1)
        self.dfu = DataFileUtil(self.callback_url)
                                  
        #for sample in sample_type:
        # should separate out sink and source samples into seperate dfs
            #if sample.[****] == params['sink_label']:
            # Want to check if sample type field is the same as sink. **** should be the index for just sample type field
                #sink_otus.append(amplicon_matrix_ref.loc[sample.[----]])
                # Place corresponding column in amplicon matrix in the sink array. ---- should be the field with the sample ID
            #if sample.[****] == params['source_label']:
            # Want to check if sample type field is the same as source. **** should be the index for just sample type field
                #source_otus.append(amplicon_matrix_ref.loc[sample.[----]])
                # Place corresponding column in amplicon matrix in the source array. ---- should be the field with the sample ID
            #else:
                #raise ValueError('Label' + sample + 'was not recognised as sink nor sample')
        
        # example source otus
        otus = np.array(['o%s' % i for i in range(50)])
        source1 = np.random.randint(0, 1000, size=50)
        source2 = np.random.randint(0, 1000, size=50)
        source3 = np.random.randint(0, 1000, size=50)
        source_df = pd.DataFrame([source1, source2, source3], index=['source1', 'source2', 'source3'], columns=otus, dtype=np.int32)
        
        # example sink otus
        sink1 = np.ceil(.5*source1+.5*source2)
        sink2 = np.ceil(.5*source2+.5*source3)
        sink3 = np.ceil(.5*source1+.5*source3)
        sink4 = source1
        sink5 = source2
        sink6 = np.random.randint(0, 1000, size=50)
        sink_df = pd.DataFrame([sink1, sink2, sink3, sink4, sink5, sink6], index=np.array(['sink%s' % i for i in range(1,7)]), columns=otus, dtype=np.int32)
        
        alpha1 = .01
        alpha2 = .001
        beta = 10
        restarts = 5
        draws_per_restart = 1
        burnin = 2
        delay = 2
        #source_df = pd.Dataframe([source_otus])
        #sink_df = pd.Dataframe([sink_otus])
        
        mpm, mps, fas = _sourcetrackerUtil.gibbs(source_df, sink_df, alpha1, alpha2, beta, restarts, draws_per_restart, burnin, delay, create_feature_tables=True)
                                  
        html_files = params.get('amplicon_matrix_ref')

        report_params = {
            'message'= 'Proportion Tables',
            'workspace_name': ws_name,
            'html_links': html_files,
            'direct_html_link_index': 0,
            'html_window_height': 333,
        }
        
        output = {
            'report_ref': report_info['ref'],
            'report_name': report_info['name'],
        }
        #END run_SourceTracker

        # At some point might do deeper type checking...
        if not isinstance(output, dict):
            raise ValueError('Method run_SourceTracker return value ' +
                             'output is not type dict as required.')
        # return the results
        return [output]
    def status(self, ctx):
        #BEGIN_STATUS
        report_output = {'state': "OK",
                     'message': "",
                     'version': self.VERSION,
                     'git_url': self.GIT_URL,
                     'git_commit_hash': self.GIT_COMMIT_HASH}
        #END_STATUS
        return [returnVal]

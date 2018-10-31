# Copyright 2018 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import time

import pytest


@pytest.fixture
def temp_dataset():
    from google.cloud import bigquery

    client = bigquery.Client()
    dataset_id = "temp_dataset_{}".format(int(time.time() * 1000))
    dataset_ref = bigquery.DatasetReference(client.project, dataset_id)
    dataset = client.create_dataset(bigquery.Dataset(dataset_ref))
    yield dataset
    client.delete_dataset(dataset, delete_contents=True)


def test_query():
    # [START bigquery_client_library_query]
    from google.cloud import bigquery

    client = bigquery.Client()
    sql = """
        SELECT name
        FROM `bigquery-public-data.usa_names.usa_1910_current`
        WHERE state = 'TX'
        LIMIT 100
    """

    # Run a Standard SQL query using the environment's default project
    df = client.query(sql).to_dataframe()

    # Run a Standard SQL query with the project set explicitly
    project_id = 'your-project-id'
    # [END bigquery_client_library_query]
    assert len(df) > 0
    project_id = os.environ['GCLOUD_PROJECT']
    # [START bigquery_client_library_query]
    df = client.query(sql, project=project_id).to_dataframe()
    # [END bigquery_client_library_query]
    assert len(df) > 0


def test_legacy_query():
    # [START bigquery_client_library_query_legacy]
    from google.cloud import bigquery

    client = bigquery.Client()
    sql = """
        SELECT name
        FROM [bigquery-public-data:usa_names.usa_1910_current]
        WHERE state = 'TX'
        LIMIT 100
    """
    query_config = bigquery.QueryJobConfig()
    query_config.use_legacy_sql = True

    # Run a Standard SQL query using the environment's default project
    df = client.query(sql, job_config=query_config).to_dataframe()
    # [END bigquery_client_library_query_legacy]
    assert len(df) > 0


def test_query_with_parameters():
    # [START bigquery_client_library_query_parameters]
    from google.cloud import bigquery

    client = bigquery.Client()
    sql = """
        SELECT name
        FROM `bigquery-public-data.usa_names.usa_1910_current`
        WHERE state = @state
        LIMIT @limit
    """
    query_config = bigquery.QueryJobConfig()
    query_config.query_parameters = [
        bigquery.ScalarQueryParameter('state', 'STRING', 'TX'),
        bigquery.ScalarQueryParameter('limit', 'INTEGER', 100)
    ]
    df = client.query(sql, job_config=query_config).to_dataframe()
    # [END bigquery_client_library_query_parameters]
    assert len(df) > 0


def test_upload_from_dataframe(temp_dataset):
    # [START bigquery_client_library_upload_from_dataframe]
    from google.cloud import bigquery
    import pandas

    df = pandas.DataFrame(
        {
            'my_string': ['a', 'b', 'c'],
            'my_int64': [1, 2, 3],
            'my_float64': [4.0, 5.0, 6.0],
        }
    )
    client = bigquery.Client()
    dataset_ref = client.dataset('my_dataset')
    # [END bigquery_client_library_upload_from_dataframe]
    dataset_ref = client.dataset(temp_dataset.dataset_id)
    # [START bigquery_client_library_upload_from_dataframe]
    table_ref = dataset_ref.table('new_table')
    client.load_table_from_dataframe(df, table_ref).result()
    # [END bigquery_client_library_upload_from_dataframe]
    client = bigquery.Client()
    table = client.get_table(table_ref)
    assert table.num_rows == 3

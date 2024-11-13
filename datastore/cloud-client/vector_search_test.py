# Copyright 2024 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import pytest

from google.cloud import datastore
from google.cloud.datastore.vector import Vector

from vector_search import store_vectors
from vector_search import vector_search_basic
from vector_search import vector_search_distance_result_field
from vector_search import vector_search_distance_threshold
from vector_search import vector_search_prefilter


os.environ["GOOGLE_CLOUD_PROJECT"] = os.environ["FIRESTORE_PROJECT"]
PROJECT_ID = os.environ["GOOGLE_CLOUD_PROJECT"]


@pytest.fixture(scope="module")
def db():
    client = datastore.Client()
    _clear_db(client)
    entity_list = add_coffee_beans_data(client)
    yield client
    for e in entity_list:
        client.delete(e)

def _clear_db(db):
    """remove all entities with kind-coffee-beans, so we have a new databse"""
    query = db.query(kind="coffee-beans")
    query.keys_only()
    keys = list(query.fetch())
    db.delete_multi(keys)


def add_coffee_beans_data(db):
    entity1 = datastore.Entity(db.key("coffee-beans", "Arabica"))
    entity1.update({"embedding_field": Vector([10.0, 1.0, 2.0]), "color": "red"})
    entity2 = datastore.Entity(db.key("coffee-beans", "Robusta"))
    entity2.update({"embedding_field": Vector([4.0, 1.0, 2.0]), "color": ""})
    entity3 = datastore.Entity(db.key("coffee-beans", "Excelsa"))
    entity3.update({"embedding_field": Vector([11.0, 1.0, 2.0]), "color": "red"})
    entity4 = datastore.Entity(db.key("coffee-beans", "Liberica"))
    entity4.update({"embedding_field": Vector([3.0, 1.0, 2.0]), "color": "green"})

    entity_list = [entity1, entity2, entity3, entity4]
    db.put_multi(entity_list)
    return entity_list

def test_store_vectors():
    # run an ensure there are no exceptions
    client, entity = store_vectors()
    client.delete(entity)

def test_vector_search_basic(db):
    vector_query = vector_search_basic(db)
    results = list(vector_query.fetch())

    assert len(results) == 4
    assert results[0].key.name == "Liberica"
    assert results[1].key.name == "Robusta"
    assert results[2].key.name == "Arabica"
    assert results[3].key.name == "Excelsa"


def test_vector_search_prefilter(db):
    vector_query = vector_search_prefilter(db)
    results = list(vector_query.fetch())

    assert len(results) == 2
    assert results[0].key.name == "Arabica"
    assert results[1].key.name == "Excelsa"


def test_vector_search_distance_result_field(db):
    vector_query = vector_search_distance_result_field(db)
    results = list(vector_query.fetch())

    assert len(results) == 4
    assert results[0].key.name == "Liberica"
    assert results[0]["vector_distance"] == 0.0
    assert results[1].key.name == "Robusta"
    assert results[1]["vector_distance"] == 1.0
    assert results[2].key.name == "Arabica"
    assert results[2]["vector_distance"] == 7.0
    assert results[3].key.name == "Excelsa"
    assert results[3]["vector_distance"] == 8.0


def test_vector_search_distance_threshold(db):
    vector_query = vector_search_distance_threshold(db)
    results = list(vector_query.fetch())

    assert len(results) == 2
    assert results[0].key.name == "Liberica"
    assert results[1].key.name == "Robusta"
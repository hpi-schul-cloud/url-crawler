"""Test the communication with the api and the server.
"""
from pytest import mark, fixture, skip
from unittest.mock import call, Mock
from collections import namedtuple
from schul_cloud_url_crawler import fetch
from pprint import pprint


RESPONSE = namedtuple("RESPONSE", ["data"])
ID = namedtuple("ID", ["id"])

def api_id(client, crawled_resource):
    """Return the id of the resource on the api as used by the client."""
    return client.client_id + ":" + crawled_resource.id


def test_delete_all_resources(client, api):
    """Test the deletion of all resources."""
    client.delete_resources()
    api.delete_resources.assert_called_once_with()


def test_update_present_resource(client, api, crawled_resource):
    """Test that the client tries to delete the resource and add it again if it is present."""
    _id = api_id(client, crawled_resource)
    post = crawled_resource.get_api_resource_post(client.client_id + ":")
    api.get_resource_ids.return_value = RESPONSE([ID(_id)])
    client.update_resource(crawled_resource)
    assert api.mock_calls == [call.get_resource_ids(), call.delete_resource(_id), call.add_resource(post)]


def test_update_nonexistent_resource(client, api, crawled_resource):
    """Test that a delete call is not issued if the resource does not exist."""
    _id = api_id(client, crawled_resource)
    post = crawled_resource.get_api_resource_post(client.client_id + ":")
    api.get_resource_ids.return_value = RESPONSE([])
    client.update_resource(crawled_resource)
    assert api.mock_calls == [call.get_resource_ids(), call.add_resource(post)]


def test_deleting_resources_from_urls(client, api, crawled_resource):
    """Test that the resources frm the urls are deleted, identified by the
    client id and the hash of the url.
    """
    _id = api_id(client, crawled_resource)
    api.get_resource_ids.return_value = RESPONSE([
        ID(_id), ID(client.client_id + ":asdad"), ID("asdasdasddsa")])
    client.delete_resources_from([crawled_resource.origin_url])
    assert api.mock_calls == [call.get_resource_ids(), call.delete_resource(_id)]


def test_deleting_resources_not_from_urls(client, api, crawled_resource):
    """Test that the resources frm the urls are deleted, identified by the
    client id and the hash of the url.
    """
    _id = api_id(client, crawled_resource)
    api.get_resource_ids.return_value = RESPONSE([
        ID(_id), ID(client.client_id + ":asdad"), ID("asdasdasddsa")])
    client.delete_resources_not_from([crawled_resource.origin_url])
    assert api.mock_calls == [call.get_resource_ids(), call.delete_resource(client.client_id + ":asdad")]


# TODO: client updates list of resource ids
#       delete deletes then
#       add them
#       -> add test that tests sequences of delete and add

class TestUpdateResources:
    """Test the update functionality"""

    def test_fetch_is_from_the_module(self, client):
        """Make sure the fetch function is imported"""
        assert client.fetch == fetch

    def test_can_mock_fetch(self, client):
        """Make sure we can mock."""
        client.fetch = mock_fetch = Mock()
        assert client.fetch == mock_fetch

    def test_update_calls_fetch(self, client, resource_urls, api):
        """The update function uses the predefined fetch function."""
        api.get_resource_ids.return_value = RESPONSE([])
        client.fetch = 	mock_fetch = Mock()
        client.update(resource_urls)
        assert len(mock_fetch.mock_calls) == 1
        assert mock_fetch.mock_calls[0][1][0] == resource_urls

    @fixture
    def fetch_mock_api(self, client, crawled_resources, api, resource_urls):
        """Make the client update the urls from the resource_urls with the
        crawled_resources by mocking fetch.

        Return the api which can be tested for calls.
        """
        if len(crawled_resources) == 0:
            skip("not enough resources!")
        _id = api_id(client, crawled_resources[0])
        api.get_resource_ids.return_value = RESPONSE([
            ID(client.client_id + ":asdsadad"), ID(_id), ID("asdasdasddsa")])
        def fetch(resource_urls, on_resource_found):
            for crawled_resource in crawled_resources:
                on_resource_found(crawled_resource)
        client.fetch = fetch
        client.update(resource_urls)
        return api

    def test_update_gets_all_ids(self, fetch_mock_api, ):
        """Fetching a needs the client ids."""
        fetch_mock_api.get_resource_ids.assert_called_once_with()

    def test_update_an_existing_resource_replaces_the_resource(
            self, fetch_mock_api, client, crawled_resources):
        """Fetching a resource replaces an existing resource."""
        _id = api_id(client, crawled_resources[0])
        fetch_mock_api.delete_resource.assert_called_once_with(_id)
        post = crawled_resources[0].get_api_resource_post(client.client_id + ":")
        pprint(fetch_mock_api.mock_calls)
        fetch_mock_api.add_resource.assert_any_call(post)

    def test_update_a_new_resource_adds_the_resource(
            self, fetch_mock_api, client, crawled_resources):
        """Fetching a resource adds a new resource."""
        _id = api_id(client, crawled_resources[0])
        for crawled_resource in crawled_resources:
            post = crawled_resource.get_api_resource_post(client.client_id + ":")
            fetch_mock_api.add_resource.assetr_any_call(post)

    def test_update_does_not_remove_resources_from_other_urls(
            self, fetch_mock_api):
        """The resources from urls which are not updated are not removed."""
        assert fetch_mock_api.delete_resource.call_count == 1












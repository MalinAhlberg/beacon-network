"""Beacon Aggregator API."""

import os
import sys
import json

import aiohttp_cors

from aiohttp import web

from endpoints.info import get_info
from endpoints.service_types import get_service_types
from endpoints.services import register_service, get_services, update_service, delete_services
from endpoints.query import send_beacon_query, send_beacon_query_websocket
from endpoints.beacons import invalidate_cache
from schemas import load_schema
from utils.utils import application_security
from utils.validate import validate, api_key
from utils.db_pool import init_db_pool
from utils.logging import LOG
from config import CONFIG

routes = web.RouteTableDef()


@routes.get('/', name='index')
async def index(request):
    """Greeting endpoint."""
    LOG.debug('Greeting endpoint.')
    return web.Response(text='GA4GH Beacon Aggregator API')


@routes.get('/query')
async def query(request):
    """Forward variant query to Beacons."""
    LOG.debug('GET /query received.')
    # Tap into the database pool
    db_pool = request.app['pool']

    # For websocket
    connection_header = request.headers.get('Connection', 'default').lower().split(',')  # break down if multiple items
    connection_header = [value.strip() for value in connection_header]  # strip spaces

    if 'upgrade' in connection_header and request.headers.get('Upgrade', 'default').lower() == 'websocket':
        # Use asynchronous websocket connection
        # Send request for processing
        websocket = await send_beacon_query_websocket(request, db_pool)

        # Return websocket connection
        return websocket
    else:
        # User standard synchronous http
        # Send request for processing
        response = await send_beacon_query(request, db_pool)

        # Return results
        return web.json_response(response)


@routes.delete('/beacons')
async def beacons(request):
    """Invalidate cached Beacons."""
    LOG.debug('DELETE /beacons received.')

    # Send request for processing
    await invalidate_cache()

    # Return confirmation
    return web.HTTPNoContent()


@routes.get('/info')
async def info(request):
    """Return service info."""
    LOG.debug('GET /info received.')
    # Tap into the database pool
    db_pool = request.app['pool']

    # Send request for processing
    response = await get_info(os.environ.get('HOST_ID', CONFIG.aggregator['host_id']), db_pool)

    # Return results
    return web.json_response(response)


@routes.get('/servicetypes')
async def service_types(request):
    """Return service types."""
    LOG.debug('GET /servicetypes received.')
    response = await get_service_types()
    return web.json_response(response)


@routes.post('/services')
@validate(load_schema("serviceinfo"))
async def services_post(request):
    """POST request to the /services endpoint.
    Register a new service at host.
    """
    LOG.debug('POST /services received.')
    # Tap into the database pool
    db_pool = request.app['pool']

    # Send request for processing
    response = await register_service(request, db_pool)

    # Return confirmation and service key if no problems occurred during processing
    return web.HTTPCreated(body=json.dumps(response), content_type='application/json')


@routes.get('/services')
@routes.get('/services/{service_id}')
async def services_get(request):
    """GET request to the /services endpoint.
    Return services that are registered at host.
    """
    LOG.debug('GET /services received.')
    # Tap into the database pool
    db_pool = request.app['pool']

    # Send request for processing
    response = await get_services(request, db_pool)

    # Return results
    return web.json_response(response)


@routes.put('/services/{service_id}')
@validate(load_schema("serviceinfo"))
async def services_put(request):
    """PATCH request to the /user endpoint.
    Update service details at host.
    """
    LOG.debug('PUT /services received.')
    # Tap into the database pool
    db_pool = request.app['pool']

    # Send request for processing
    await update_service(request, db_pool)

    # Return confirmation
    return web.HTTPNoContent()


@routes.delete('/services')
@routes.delete('/services/{service_id}')
async def services_delete(request):
    """DELETE request to the /user endpoint.
    Delete registered service from host.
    """
    LOG.debug('DELETE /services received.')
    # Tap into the database pool
    db_pool = request.app['pool']

    # Send request for processing
    await delete_services(request, db_pool)

    # Return confirmation
    return web.HTTPNoContent()


async def init_db(app):
    """Initialise a database connection pool."""
    LOG.info('Creating database connection pool.')
    app['pool'] = await init_db_pool(host=os.environ.get('DB_HOST', CONFIG.aggregator.get('db_host', 'localhost')),
                                     port=os.environ.get('DB_PORT', CONFIG.aggregator.get('db_port', '5432')),
                                     user=os.environ.get('DB_USER', CONFIG.aggregator.get('db_user', 'user')),
                                     passwd=os.environ.get('DB_PASS', CONFIG.aggregator.get('db_pass', 'pass')),
                                     db=os.environ.get('DB_NAME', CONFIG.aggregator.get('db_name', 'db')))


async def close_db(app):
    """Close the database connection pool."""
    LOG.info('Closing database connection pool.')
    await app['pool'].close()


def set_cors(app):
    """Set CORS rules."""
    LOG.debug('Applying CORS rules.')
    # Configure CORS settings, allow all domains
    cors = aiohttp_cors.setup(app, defaults={
        "*": aiohttp_cors.ResourceOptions(
            allow_credentials=True,
            expose_headers="*",
            allow_headers="*",
        )
    })
    # Apply CORS to endpoints
    for route in list(app.router.routes()):
        cors.add(route)


def init_app():
    """Initialise the web server."""
    LOG.info('Initialising web server.')
    app = web.Application(middlewares=[api_key()])
    app.router.add_routes(routes)
    set_cors(app)
    app.on_startup.append(init_db)
    app.on_cleanup.append(close_db)
    return app


def main():
    """Run the web server."""
    LOG.info('Starting server build.')
    web.run_app(init_app(),
                host=os.environ.get('APP_HOST', CONFIG.aggregator.get('app_host', '0.0.0.0')),
                port=int(os.environ.get('APP_PORT', CONFIG.aggregator.get('app_port', 8080))),
                shutdown_timeout=0,
                ssl_context=application_security())


if __name__ == '__main__':
    assert sys.version_info >= (3, 6), "This service requires python3.6 or above"
    LOG.info('Starting web server start-up routines.')
    main()

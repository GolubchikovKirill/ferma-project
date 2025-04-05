from api.router_acc import router as account
from api.router_proxy import router as proxy
from api.router_channel import router as channel
from api.schema_html import router as schema_html
from api.router_yandex import router as yandex
from api.router_commenting import router as commenting

routers = [account, proxy, channel, schema_html, yandex, commenting]
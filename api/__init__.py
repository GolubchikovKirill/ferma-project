from routers.router_acc import router as account
from routers.router_proxy import router as proxy
from routers.router_channel import router as channel
from routers.router_html import router as schema_html
from routers.router_yandex import router as yandex
from routers.router_commenting import router as commenting

routers = [account, proxy, channel, schema_html, yandex, commenting]
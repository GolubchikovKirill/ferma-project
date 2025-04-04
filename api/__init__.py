from api.router_acc import router as account
from api.router_proxy import router as proxy
from api.router_channel import router as channel
from api.schema_html import router as schema_html

routers = [account, proxy, channel, schema_html]
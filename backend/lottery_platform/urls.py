"""
主URL配置
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

# 导入自定义管理后台
from apps.core.admin import admin_site

urlpatterns = [
    # 使用自定义管理后台
    path('admin/', admin_site.urls),
    # 保留默认管理后台作为备用
    path('django-admin/', admin.site.urls),
    
    # API文档
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    
    # API路由
    path('api/v1/auth/', include('apps.users.urls')),
    path('api/v1/finance/', include('apps.finance.urls')),
    path('api/v1/games/', include('apps.games.urls')),
    path('api/v1/rewards/', include('apps.rewards.urls')),
    path('api/v1/sports/', include('apps.games.sports.urls')),
    
    # 性能监控
    path('silk/', include('silk.urls', namespace='silk')),
]

# 开发环境静态文件服务
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
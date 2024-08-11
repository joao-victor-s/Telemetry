from metrics.views.car_map import CarMapView
from shared.store.store import MetricStore

views_list = [CarMapView]
views_dict = {view.NAMESPACE: view for view in views_list}
view_namespaces = frozenset([view.NAMESPACE for view in views_list])


async def apply_view(view_namespace: str, view_params: dict, metric_store: MetricStore):
    view = views_dict[view_namespace](**view_params)
    metrics = view.depends_on()
    snapshots = await metric_store.get_snapshots(metrics)
    snapshots_dict = {snap[0]: snap for snap in snapshots}
    view_data = view.process(snapshots_dict)
    return view_data


del MetricStore

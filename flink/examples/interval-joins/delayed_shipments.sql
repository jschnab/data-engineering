select *
from orders o, shipments s
where o.order_id = s.order_id and s.shipment_timestamp > o.order_timestamp + interval '4' hours
;

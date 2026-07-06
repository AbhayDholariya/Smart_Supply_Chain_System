import { Link } from "react-router-dom";
import { Table, Thead, Th, Tbody, Tr, Td } from "@/components/ui/Table";
import ShipmentStatusBadge from "./ShipmentStatusBadge";
import { formatDate } from "@/utils/formatDate";
import type { Shipment } from "@/types/shipment";

interface Props {
  shipments: Shipment[];
}

export default function ShipmentTable({ shipments }: Props) {
  return (
    <Table>
      <Thead>
        <tr>
          <Th>Tracking #</Th>
          <Th>Origin</Th>
          <Th>Destination</Th>
          <Th>Status</Th>
          <Th>Carrier</Th>
          <Th>Est. Delivery</Th>
        </tr>
      </Thead>
      <Tbody>
        {shipments.map((s) => (
          <Tr key={s.id}>
            <Td>
              <Link
                to={`/shipments/${s.id}`}
                className="font-medium text-primary-600 hover:underline"
              >
                {s.tracking_number}
              </Link>
            </Td>
            <Td>{s.origin}</Td>
            <Td>{s.destination}</Td>
            <Td>
              <ShipmentStatusBadge status={s.status} />
            </Td>
            <Td>{s.carrier || "—"}</Td>
            <Td>{s.estimated_delivery ? formatDate(s.estimated_delivery) : "—"}</Td>
          </Tr>
        ))}
      </Tbody>
    </Table>
  );
}

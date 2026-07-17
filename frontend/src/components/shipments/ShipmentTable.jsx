
import { Link } from "react-router-dom";
import { Table, Thead, Th, Tbody, Tr, Td } from "@/components/ui/Table";
import ShipmentStatusBadge from "./ShipmentStatusBadge";
import { formatDate } from "@/utils/formatDate";

export default function ShipmentTable({ shipments }) {
  return (
    <Table>
      <Thead>
        <tr>
          <Th>Tracking #</Th>
          <Th>Origin</Th>
          <Th>Destination</Th>
          <Th>Status</Th>
          <Th>Risk Score</Th>
          <Th>Carrier</Th>
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
                {s.id}
              </Link>
            </Td>
            <Td>{s.origin}</Td>
            <Td>{s.destination}</Td>
            <Td>
              <ShipmentStatusBadge status={s.status} />
            </Td>
            <Td style={{ color: s.risk_score > 70 ? "red" : s.risk_score > 40 ? "orange" : "green" }}>
              {s.risk_score}
            </Td>
            <Td>{s.carrier || "—"}</Td>
          </Tr>
        ))}
      </Tbody>
    </Table>
  );
}

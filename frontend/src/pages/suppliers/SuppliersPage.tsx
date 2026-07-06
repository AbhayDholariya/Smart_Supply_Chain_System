import { useSuppliers } from "@/hooks/useSuppliers";
import { Table, Thead, Th, Tbody, Tr, Td } from "@/components/ui/Table";
import Badge from "@/components/ui/Badge";
import Spinner from "@/components/ui/Spinner";

export default function SuppliersPage() {
  const { data, isLoading } = useSuppliers();

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold text-gray-900">Suppliers</h1>

      {isLoading ? (
        <div className="flex justify-center py-20">
          <Spinner />
        </div>
      ) : (
        <Table>
          <Thead>
            <tr>
              <Th>Name</Th>
              <Th>Email</Th>
              <Th>Country</Th>
              <Th>Performance</Th>
              <Th>On-Time Rate</Th>
              <Th>Status</Th>
            </tr>
          </Thead>
          <Tbody>
            {data?.results.map((s) => (
              <Tr key={s.id}>
                <Td className="font-medium">{s.name}</Td>
                <Td>{s.contact_email}</Td>
                <Td>{s.country || "—"}</Td>
                <Td>
                  <span
                    className={
                      s.performance_score >= 80
                        ? "text-green-600 font-semibold"
                        : s.performance_score >= 60
                        ? "text-yellow-600 font-semibold"
                        : "text-red-600 font-semibold"
                    }
                  >
                    {s.performance_score.toFixed(1)}
                  </span>
                </Td>
                <Td>{(s.on_time_delivery_rate * 100).toFixed(1)}%</Td>
                <Td>
                  {s.is_active ? (
                    <Badge label="Active" className="bg-green-100 text-green-700" />
                  ) : (
                    <Badge label="Inactive" className="bg-gray-100 text-gray-600" />
                  )}
                </Td>
              </Tr>
            ))}
          </Tbody>
        </Table>
      )}
    </div>
  );
}

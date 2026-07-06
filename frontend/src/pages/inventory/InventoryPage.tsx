import { useInventoryItems } from "@/hooks/useInventory";
import { Table, Thead, Th, Tbody, Tr, Td } from "@/components/ui/Table";
import Badge from "@/components/ui/Badge";
import Spinner from "@/components/ui/Spinner";

export default function InventoryPage() {
  const { data, isLoading } = useInventoryItems();

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold text-gray-900">Inventory</h1>

      {isLoading ? (
        <div className="flex justify-center py-20">
          <Spinner />
        </div>
      ) : (
        <Table>
          <Thead>
            <tr>
              <Th>SKU</Th>
              <Th>Product</Th>
              <Th>Warehouse</Th>
              <Th>Quantity</Th>
              <Th>Reorder At</Th>
              <Th>Status</Th>
            </tr>
          </Thead>
          <Tbody>
            {data?.results.map((item) => (
              <Tr key={item.id}>
                <Td className="font-mono text-xs">{item.product}</Td>
                <Td>{item.product_name}</Td>
                <Td>{item.warehouse_name}</Td>
                <Td className="font-semibold">{item.quantity}</Td>
                <Td>{item.reorder_threshold}</Td>
                <Td>
                  {item.is_low_stock ? (
                    <Badge label="Low Stock" className="bg-red-100 text-red-700" />
                  ) : (
                    <Badge label="OK" className="bg-green-100 text-green-700" />
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

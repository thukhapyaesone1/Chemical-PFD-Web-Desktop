import React, { useState } from "react";
import { Button, Card, CardBody } from "@heroui/react";
// import { generateEquipmentReport } from "@/utils/reportUtils";

interface Equipment {
  slNo: number;
  tagNo: string;
  type: string;
  description: string;
}

// Sample data
const equipmentList: Equipment[] = [
  { slNo: 1, tagNo: "P-01-A/B", type: "Hand Pump", description: "Hand Pump with Drum" },
  { slNo: 2, tagNo: "P-02-A/B", type: "Reciprocating Pump", description: "" },
  { slNo: 3, tagNo: "E-01", type: "Heat Exchanger", description: "" },
  { slNo: 4, tagNo: "P-03-A/B", type: "Hand Pump", description: "Hand Pump with Drum" },
  { slNo: 5, tagNo: "P-04-A/B", type: "Proportioning Pump", description: "" },
  { slNo: 6, tagNo: "P-05-A/B", type: "Proportioning Pump", description: "" },
  { slNo: 7, tagNo: "C-01-A/B", type: "Centrifugal Compressor", description: "" },
  { slNo: 8, tagNo: "C-02-A/B", type: "Turbine", description: "" },
  { slNo: 9, tagNo: "PRV-01-A/B", type: "Gate Valve", description: "" },
  { slNo: 10, tagNo: "SR-01", type: "Jaw Crusher", description: "" },
];

export default function ReportsPage() {
  const [isGenerating, setIsGenerating] = useState(false);

  const handleGenerateReport = async () => {
    setIsGenerating(true);
    // try {
    //   await generateEquipmentReport(equipmentList);
    // } catch (err) {
    //   console.error("Failed to generate report", err);
    // } finally {
    //   setIsGenerating(false);
    // }
  };

  return (
    <div className="p-6 bg-gray-50 dark:bg-gray-900 min-h-screen">
      <h1 className="text-2xl font-semibold text-gray-800 dark:text-gray-200 mb-6">
        Equipment Reports
      </h1>

      <div className="mb-6">
        <Button 
          size="sm"
          onPress={handleGenerateReport}
          isLoading={isGenerating}
        >
          Generate PDF Report
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {equipmentList.map((item) => (
          <Card key={item.slNo} className="bg-white dark:bg-gray-800">
            <CardBody className="p-4">
              <div className="text-sm font-medium text-gray-700 dark:text-gray-200">
                {item.tagNo} - {item.type}
              </div>
              <div className="text-xs text-gray-500 mt-1">{item.description}</div>
              <div className="text-xs text-gray-400 mt-1">Sl No: {item.slNo}</div>
            </CardBody>
          </Card>
        ))}
      </div>
    </div>
  );
}

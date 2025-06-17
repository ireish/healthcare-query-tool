import React, { useMemo } from "react";
import {
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  CartesianGrid,
} from "recharts";
import { PatientChartsProps, PatientDisplayData } from "@/types";
import { topNWithOther } from "@/lib/utils";

const COLORS = [
  "#8884d8",
  "#82ca9d",
  "#ffc658",
  "#ff8042",
  "#8dd1e1",
  "#a4de6c",
];

export default function PatientCharts({ patients }: PatientChartsProps) {
  // Gender distribution data
  const genderData = useMemo(() => {
    const counts: Record<string, number> = { Male: 0, Female: 0, Other: 0 };
    patients.forEach((p) => {
      let key = p.gender || "Other";
      if (key !== "Male" && key !== "Female") key = "Other";
      counts[key] = (counts[key] || 0) + 1;
    });
    return Object.entries(counts).map(([name, value]) => ({ name, value }));
  }, [patients]);

  // Age distribution data with custom age brackets
  const ageData = useMemo(() => {
    const counts: Record<string, number> = {
      "0-18": 0,
      "19-30": 0,
      "31-45": 0,
      "46-60": 0,
      "60-80": 0,
      ">80": 0,
      "Unknown": 0
    };
    
    patients.forEach((p) => {
      if (p.age === "-") {
        counts["Unknown"]++;
        return;
      }
      const ageNum = parseInt(p.age, 10);
      if (isNaN(ageNum)) {
        counts["Unknown"]++;
        return;
      }
      
      if (ageNum <= 18) counts["0-18"]++;
      else if (ageNum <= 30) counts["19-30"]++;
      else if (ageNum <= 45) counts["31-45"]++;
      else if (ageNum <= 60) counts["46-60"]++;
      else if (ageNum <= 80) counts["60-80"]++;
      else counts[">80"]++;
    });
    
    // Return all brackets (no need to limit to top N since we have predefined categories)
    return Object.entries(counts).map(([name, value]) => ({ name, value }));
  }, [patients]);

  // Country distribution data
  const countryData = useMemo(() => {
    const counts: Record<string, number> = {};
    patients.forEach((p) => {
      const country = p.country && p.country !== "-" ? p.country : "Unknown";
      counts[country] = (counts[country] || 0) + 1;
    });
    return topNWithOther(counts, 5);
  }, [patients]);

  if (!patients.length) {
    return null;
  }

  return (
    <div className="w-full max-w-7xl mx-auto mt-8 grid grid-cols-1 md:grid-cols-2 gap-6">
      {/* Gender Distribution */}
      <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200 flex flex-col items-center">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">Gender Distribution</h3>
        <ResponsiveContainer width="100%" height={300}>
          <PieChart>
            <Pie
              data={genderData}
              dataKey="value"
              nameKey="name"
              innerRadius={60}
              outerRadius={100}
              paddingAngle={3}
              label
            >
              {genderData.map((entry, index) => (
                <Cell key={`cell-gender-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip />
            <Legend verticalAlign="bottom" height={36} />
          </PieChart>
        </ResponsiveContainer>
      </div>

      {/* Age Distribution */}
      <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200 flex flex-col items-center">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">Age Distribution</h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={ageData} margin={{ top: 20, right: 20, left: 0, bottom: 20 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" label={{ value: "Age Bracket", position: "insideBottom", offset: -10 }} />
            <YAxis allowDecimals={false} />
            <Tooltip />
            <Bar dataKey="value" fill="#8884d8">
              {ageData.map((entry, index) => (
                <Cell key={`cell-age-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Country Distribution */}
      <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200 md:col-span-2 flex flex-col items-center">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">Top Countries</h3>
        <ResponsiveContainer width="100%" height={400}>
          <BarChart layout="vertical" data={countryData} margin={{ top: 20, right: 40, left: 20, bottom: 20 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis type="number" allowDecimals={false} />
            <YAxis type="category" dataKey="name" width={120} />
            <Tooltip />
            <Bar dataKey="value" fill="#82ca9d">
              {countryData.map((entry, index) => (
                <Cell key={`cell-country-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
} 
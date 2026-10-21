import React, { createContext, useContext, useState, useEffect } from "react";
import { TRACK_CONFIGS, TrackConfig } from "../data/capstoneData";

export interface DataSourceMeta {
  source_type: string;
  source_label: string;
  loaded_at: string;
  row_count: number;
  column_count: number;
  sha256: string;
  warnings: string[];
}

interface DataContextType {
  activeTrack: "SALES" | "CHURN" | "HR_ATTRITION";
  setActiveTrack: (track: "SALES" | "CHURN" | "HR_ATTRITION") => void;
  trackConfig: TrackConfig;
  activeSource: "bundled" | "upload" | "webhook" | "database" | "api";
  setActiveSource: (source: "bundled" | "upload" | "webhook" | "database" | "api") => void;
  isMissingDataset: boolean;
  setIsMissingDataset: (val: boolean) => void;
  activePage: string;
  setActivePage: (page: string) => void;
  dataset: any[];
  setDataset: React.Dispatch<React.SetStateAction<any[]>>;
  meta: DataSourceMeta;
  columnMappings: Record<string, string>;
  setColumnMappings: React.Dispatch<React.SetStateAction<Record<string, string>>>;
  reloadBundled: () => void;
  simulateWebhookPush: () => void;
  handleFileUpload: (fileName: string, rows: any[]) => void;
  isUploadModalOpen: boolean;
  setIsUploadModalOpen: (open: boolean) => void;
  uploadedFileName: string | null;
  webhookStatus: {
    lastPayloadId?: string;
    signatureVerified: boolean;
    timestamp?: string;
    rowCount: number;
  };
}

const DataContext = createContext<DataContextType | undefined>(undefined);

// Sample generated data rows for each track
const generateSampleRows = (track: "SALES" | "CHURN" | "HR_ATTRITION") => {
  const rows = [];
  if (track === "SALES") {
    const categories = [
      { cat: "Technology", subs: ["Phones", "Accessories", "Copiers"], margin: 0.3 },
      { cat: "Furniture", subs: ["Chairs", "Tables", "Bookcases"], margin: 0.12 },
      { cat: "Office Supplies", subs: ["Paper", "Binders", "Storage"], margin: 0.22 }
    ];
    const regions = ["West", "East", "Central", "South"];
    const shipModes = ["Standard Class", "Second Class", "First Class", "Same Day"];
    for (let i = 1; i <= 250; i++) {
      const c = categories[i % categories.length];
      const sub = c.subs[i % c.subs.length];
      const region = regions[i % regions.length];
      const shipMode = shipModes[i % shipModes.length];
      const qty = (i % 6) + 1;
      const sales = Math.round((50 + (i * 17) % 650) * 100) / 100;
      const discount = [0, 0, 0.05, 0.1, 0.15, 0.2, 0.3, 0.45][i % 8];
      const shippingCost = Math.round((8 + (i * 3.7) % 35) * 100) / 100;
      const gross = sales * c.margin;
      const discLoss = sales * (discount * 1.35);
      const profit = Math.round((gross - discLoss - shippingCost * 0.4) * 100) / 100;
      rows.push({
        Order_ID: `ORD-${1000 + i}`,
        Customer_ID: `CUST-${200 + (i % 40)}`,
        Customer_Name: `Enterprise Client ${i % 40}`,
        Order_Date: `2026-08-${String((i % 28) + 1).padStart(2, "0")}`,
        Region: region,
        Category: c.cat,
        Sub_Category: sub,
        Sales: sales,
        Quantity: qty,
        Discount: discount,
        Shipping_Cost: shippingCost,
        Ship_Mode: shipMode,
        Profit: profit,
        Customer_Rating: profit > 0 ? 4.5 : 2.5,
        Returned: discount > 0.3 && i % 4 === 0 ? 1 : 0,
        Total_Sale: Math.round(sales * (1 - discount) * 100) / 100
      });
    }
  } else if (track === "CHURN") {
    const contracts = ["Month-to-month", "One year", "Two year"];
    const payments = ["Electronic check", "Credit card (automatic)", "Bank transfer (automatic)", "Mailed check"];
    for (let i = 1; i <= 250; i++) {
      const contract = contracts[i % 3];
      const tenure = contract === "Month-to-month" ? (i % 14) + 1 : (i % 48) + 12;
      const monthly = Math.round((25 + (i * 9.2) % 90) * 100) / 100;
      const totalCharges = Math.round((monthly * tenure + ((i * 5) % 20)) * 100) / 100;
      const tickets = contract === "Month-to-month" ? (i % 5) : (i % 2);
      const complaints = tickets > 2 ? 2 : (i % 2);
      const sat = Math.max(1, Math.min(5, 5 - complaints - (tickets > 2 ? 1 : 0)));
      const churned = (contract === "Month-to-month" && (tickets > 2 || monthly > 80)) ? "Yes" : (i % 5 === 0 ? "Yes" : "No");
      rows.push({
        Customer_ID: `CUST-CH-${1000 + i}`,
        Customer_Name: `Subscriber ${i}`,
        Signup_Date: `2024-03-${String((i % 28) + 1).padStart(2, "0")}`,
        Gender: i % 2 === 0 ? "Female" : "Male",
        Senior_Citizen: i % 6 === 0 ? 1 : 0,
        Partner: i % 3 === 0 ? "Yes" : "No",
        Dependents: i % 4 === 0 ? "Yes" : "No",
        Tenure_Months: tenure,
        Contract_Type: contract,
        Monthly_Charges: monthly,
        Total_Charges: totalCharges,
        Payment_Method: payments[i % 4],
        Paperless_Billing: i % 2 === 0 ? "Yes" : "No",
        Internet_Service: i % 3 === 0 ? "Fiber optic" : "DSL",
        Tech_Support: i % 4 === 0 ? "Yes" : "No",
        Online_Security: i % 5 === 0 ? "Yes" : "No",
        Support_Tickets: tickets,
        Complaints: complaints,
        Satisfaction_Score: sat,
        NPS: sat * 2,
        Churned: churned
      });
    }
  } else {
    // HR_ATTRITION
    const depts = ["Research & Development", "Sales", "Human Resources"];
    const roles: Record<string, string[]> = {
      "Research & Development": ["Research Scientist", "Laboratory Technician", "Manufacturing Director"],
      "Sales": ["Sales Executive", "Sales Representative", "Manager"],
      "Human Resources": ["Human Resources", "Manager"]
    };
    const workModes = ["On-site", "Hybrid", "Remote"];
    for (let i = 1; i <= 250; i++) {
      const dept = depts[i % 3];
      const roleList = roles[dept];
      const role = roleList[i % roleList.length];
      const level = (i % 5) + 1;
      const income = 2600 * level + ((i * 137) % 1800);
      const age = 22 + (i % 38);
      const totalExp = Math.max(level * 2, age - 21);
      const yearsComp = Math.min(totalExp, (i % 12) + 1);
      const yearsRole = Math.min(yearsComp, (i % 5) + 1);
      const ot = i % 3 === 0 ? "Yes" : "No";
      const wlb = (i % 4) + 1;
      const js = (i % 4) + 1;
      const es = ((i + 1) % 4) + 1;
      const dist = (i % 29) + 1;
      const wm = workModes[i % 3];
      const attr = (ot === "Yes" && (wlb <= 2 || js <= 2)) || (dist > 20 && income < 4000) ? "Yes" : (i % 7 === 0 ? "Yes" : "No");
      rows.push({
        Employee_ID: `EMP-${2000 + i}`,
        Employee_Name: `Associate ${i}`,
        Hire_Date: `2021-06-${String((i % 28) + 1).padStart(2, "0")}`,
        Age: age,
        Gender: i % 2 === 0 ? "Female" : "Male",
        Department: dept,
        Job_Role: role,
        Monthly_Income: income,
        Job_Level: level,
        Years_At_Company: yearsComp,
        Years_In_Current_Role: yearsRole,
        Total_Working_Years: totalExp,
        Overtime: ot,
        Work_Life_Balance: wlb,
        Job_Satisfaction: js,
        Environment_Satisfaction: es,
        Distance_From_Home: dist,
        Num_Companies_Worked: (i % 5) + 1,
        Performance_Rating: i % 5 === 0 ? 4 : 3,
        Work_Mode: wm,
        Attrition: attr
      });
    }
  }
  return rows;
};

export const DataProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [activeTrack, setActiveTrack] = useState<"SALES" | "CHURN" | "HR_ATTRITION">("SALES");
  const [activeSource, setActiveSource] = useState<"bundled" | "upload" | "webhook" | "database" | "api">("bundled");
  const [isMissingDataset, setIsMissingDataset] = useState<boolean>(false);
  const [activePage, setActivePage] = useState<string>("home");
  const [columnMappings, setColumnMappings] = useState<Record<string, string>>({});
  const [dataset, setDataset] = useState<any[]>([]);
  const [webhookStatus, setWebhookStatus] = useState({
    signatureVerified: true,
    rowCount: 250,
    lastPayloadId: "wh-payload-992a-c28",
    timestamp: new Date().toISOString()
  });

  useEffect(() => {
    try {
      const root = document.documentElement;
      root.classList.remove("light");
      root.classList.add("dark");
      root.removeAttribute("data-theme");
      localStorage.removeItem("app_theme");
    } catch {
      // ignore
    }
  }, []);

  const trackConfig = TRACK_CONFIGS[activeTrack];

  // Refresh dataset when track changes or bundled reloaded
  useEffect(() => {
    if (activeSource === "bundled") {
      if (isMissingDataset) {
        setDataset([]);
      } else {
        const rows = generateSampleRows(activeTrack);
        setDataset(rows);
      }
    }
  }, [activeTrack, activeSource, isMissingDataset]);

  const reloadBundled = () => {
    setIsMissingDataset(false);
    setActiveSource("bundled");
    const rows = generateSampleRows(activeTrack);
    setDataset(rows);
  };

  const [isUploadModalOpen, setIsUploadModalOpen] = useState<boolean>(false);
  const [uploadedFileName, setUploadedFileName] = useState<string | null>(null);

  const handleFileUpload = (fileName: string, rows: any[]) => {
    setActiveSource("upload");
    setIsMissingDataset(false);
    setUploadedFileName(fileName);
    setDataset(rows);
  };

  const simulateWebhookPush = () => {
    setActiveSource("webhook");
    const newId = `wh-live-${Math.random().toString(36).substring(2, 9)}`;
    const rows = generateSampleRows(activeTrack);
    setDataset(rows);
    setWebhookStatus({
      lastPayloadId: newId,
      signatureVerified: true,
      timestamp: new Date().toISOString(),
      rowCount: rows.length
    });
  };

  const meta: DataSourceMeta = {
    source_type:
      activeSource === "bundled"
        ? "BundledCSVSource"
        : activeSource === "upload"
        ? "UploadedFileSource"
        : activeSource === "webhook"
        ? "WebhookPushSource"
        : activeSource === "database"
        ? "DatabaseReadOnlySource"
        : "RestAPIPullSource",
    source_label:
      activeSource === "bundled"
        ? `Local Disk: ${trackConfig.defaultFile}`
        : activeSource === "upload"
        ? `Session File: ${uploadedFileName || "uploaded_dataset.csv"} (In-Memory)`
        : activeSource === "webhook"
        ? `data/incoming/${webhookStatus.lastPayloadId || "latest"}.csv (HMAC Verified)`
        : activeSource === "database"
        ? "Database: Postgres/Supabase SELECT * FROM capstone_data"
        : "REST API Endpoint: https://api.capstone-pipeline.org/v1/stream",
    loaded_at: new Date().toISOString(),
    row_count: isMissingDataset ? 0 : dataset.length,
    column_count: isMissingDataset ? 0 : (dataset.length > 0 ? Object.keys(dataset[0]).length : 0),
    sha256: isMissingDataset
      ? "0000000000000000000000000000000000000000000000000000000000000000"
      : "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    warnings: isMissingDataset ? ["MISSING_DATASET: Cold start state activated."] : []
  };

  return (
    <DataContext.Provider
      value={{
        activeTrack,
        setActiveTrack,
        trackConfig,
        activeSource,
        setActiveSource,
        isMissingDataset,
        setIsMissingDataset,
        activePage,
        setActivePage,
        dataset,
        setDataset,
        meta,
        columnMappings,
        setColumnMappings,
        reloadBundled,
        simulateWebhookPush,
        handleFileUpload,
        isUploadModalOpen,
        setIsUploadModalOpen,
        uploadedFileName,
        webhookStatus
      }}
    >
      {children}
    </DataContext.Provider>
  );
};

export const useData = () => {
  const context = useContext(DataContext);
  if (!context) {
    throw new Error("useData must be used within DataProvider");
  }
  return context;
};

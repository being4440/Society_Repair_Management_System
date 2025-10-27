USE society_db;

-- =========================
-- 🧩 SOCIETY ADMIN
-- =========================
INSERT INTO society_admin (Admin_ID, Admin_Name, Email, Contact_No, registration_no, password_hash) VALUES
('AD_A1', 'Admin A1', 'adma1@example.com', '9999999999', 'REG', '55c098f83a46b72cf951ea43b828349d0fb118ecc1966af891e8cf950c2567af'),
('AD_A2', 'Admin A2', 'adma2@example.com', '9999999999', 'REG', '55c098f83a46b72cf951ea43b828349d0fb118ecc1966af891e8cf950c2567af'),
('AD_B1', 'Admin B1', 'admb1@example.com', '9999999999', 'REG', '55c098f83a46b72cf951ea43b828349d0fb118ecc1966af891e8cf950c2567af'),
('AD_C1', 'Admin C1', 'admc1@example.com', '9999999999', 'REG', '55c098f83a46b72cf951ea43b828349d0fb118ecc1966af891e8cf950c2567af'),
('AD_C2', 'Admin C2', 'admc2@example.com', '9999999999', 'REG', '55c098f83a46b72cf951ea43b828349d0fb118ecc1966af891e8cf950c2567af'),
('AD_D1', 'Admin D1', 'admd1@example.com', '9999999999', 'REG', '55c098f83a46b72cf951ea43b828349d0fb118ecc1966af891e8cf950c2567af'),
('AD_E1', 'Admin E1', 'adme1@example.com', '9999999999', 'REG', '55c098f83a46b72cf951ea43b828349d0fb118ecc1966af891e8cf950c2567af'),
-- =========================
-- 👥 RESIDENTS
-- =========================
INSERT INTO resident (Resident_ID, Resident_Name, Email, Contact_No, Block_name, Flat_No, password_hash) VALUES
('RS_A001', 'Amit Shah', 'amit1@example.com', '9000000001', 'A', 101, '91ee456e95ddc9a3ff2c52ab1c3ff07e5eb9eb76a4f8aad2d4b31ed97153c820'),
('RS_A002', 'Anita Joshi', 'anita2@example.com', '9000000002', 'A', 102, '5ac613b74ec49ab3ac9c10102d8efd2a98adc1b97d680f2f21423a5268c35fd9'),
('RS_A003', 'Arun Iyer', 'arun3@example.com', '9000000003', 'A', 103, '3c920558cbe8e0ae083e3c2df7aef8270aa72199a613bed640a33ced7aaac5ea'),
('RS_B001', 'Bhavna Rao', 'bhavna1@example.com', '9000001001', 'B', 201, 'd834f7cd3984ea6a53f14bc7583650237c39dbc9bae5d359c3af6e58c7fce775'),
('RS_B002', 'Brijesh Patel', 'brijesh2@example.com', '9000001002', 'B', 202, '77588c748b3598ef7eeed6b125ca49d8f366f6c482e5a125becbafa1a0e6a9cc'),
('RS_C001', 'Chitra Nair', 'chitra1@example.com', '9000002001', 'C', 301, '7d6b9e1d8f1cb774f044bc9e877fa138e38af85d931d6729556f9e9980dc7023'),
('RS_D001', 'Deepak Rao', 'deepak1@example.com', '9000003001', 'D', 401, '365e76d471146e0c6f731ac3384ef16475ea888c3217ecdc2fcd3a5291a09b79'),
('RS_E001', 'Esha Reddy', 'esha1@example.com', '9000004001', 'E', 501, '68b269d85742854cc0e9f8cbc60a7061d9fc425185cafc3fce09d32b62f8b9ab');

-- =========================
-- 🧰 REPAIR PERSONNEL
-- =========================
INSERT INTO repair_personnel (Personnel_ID, Personnel_Name, Email, Contact_No, Specialization, Is_Available) VALUES
('RP001', 'Ramesh Kumar', 'ramesh.kumar@repairsociety.com', '9876543101', 'Electrician', 1),
('RP002', 'Suresh Naik', 'suresh.naik@repairsociety.com', '9876543102', 'Plumber', 0),
('RP003', 'Ajay Patil', 'ajay.patil@repairsociety.com', '9876543103', 'Carpenter', 1),
('RP004', 'Mahesh Desai', 'mahesh.desai@repairsociety.com', '9876543104', 'Painter', 1),
('RP005', 'Kiran Joshi', 'kiran.joshi@repairsociety.com', '9876543105', 'Cleaner', 1),
('RP006', 'Arun Pawar', 'arun.pawar@repairsociety.com', '9876543201', 'Electrician', 0),
('RP007', 'Bharat Singh', 'bharat.singh@repairsociety.com', '9876543202', 'Plumber', 1),
('RP008', 'Ravi Shetty', 'ravi.shetty@repairsociety.com', '9876543203', 'Carpenter', 1),
('RP009', 'Nilesh Jadhav', 'nilesh.jadhav@repairsociety.com', '9876543204', 'Painter', 0),
('RP010', 'Vijay Shah', 'vijay.shah@repairsociety.com', '9876543205', 'Cleaner', 1);

-- =========================
-- 🧾 REPAIR REQUESTS
-- =========================
INSERT INTO repair_request (Request_ID, Resident_ID, Admin_ID, Personnel_ID, Req_Status, Issue_Description, Req_Date, Completion_Date, Created_At) VALUES
('RQ0001', 'RS_A002', 'AD_A1', 'P001', 'Assigned', 'Bathroom leaking from overhead pipe in flat 102. Needs urgent fix.', '2025-10-10', NULL, '2025-10-27 21:40:39'),
('RQ0002', 'RS_B005', 'AD_B2', NULL, 'Pending', 'Power fluctuation and frequent fuse trips in flat 205.', '2025-10-11', NULL, '2025-10-27 21:40:39'),
('RQ0003', 'RS_C009', 'AD_C1', 'P003', 'Completed', 'Kitchen cabinet door broken; needs carpentry.', '2025-09-25', '2025-09-27', '2025-10-27 21:40:39'),
('RQ0004', 'RS_D001', 'AD_D2', 'P002', 'In Progress', 'Living room lights not working, possible wiring issue.', '2025-10-01', NULL, '2025-10-27 21:40:39'),
('RQ0005', 'RS_E010', 'AD_E1', 'P007', 'Completed', 'Deep cleaning required after water seepage in balcony.', '2025-08-15', '2025-08-16', '2025-10-27 21:40:39'),
('RQ215254', 'RS_A001', NULL, NULL, 'Pending', 'Leaking water tap in bathroom , continously', '2025-10-27', NULL, '2025-10-27 21:52:54');

import mssql_python 
 
server1 = r"10.20.53.37\EXAMDSQL" 
server2 = r"10.20.53.237\RESULT" 
server3 = r"10.20.67.199,1018" 
 
 
print("===================server 1=======================") 
conn = mssql_python.connect( 
    f"Server={server1};" 
    f"Database=master;" 
    f"UID=importer;" 
    f"PWD=importer;" 
    "TrustServerCertificate=yes;" 
) 
cursor = conn.cursor() 
 
cursor.execute("""SELECT name FROM master.sys.DATABASES WITH(NOLOCK) WHERE state=0 and name IN ('B_LIB_20','BA_19','BA_2019','BALLB_17','BArch_2015','BArch_2019','LLB_23','BALLB_23','LLM_2025','Scaling_Course','BBA_19','BBA_CA_19','BBA_IB_19','BCA_SCIENCE_19','BCOM_19','BEd_15','BHMCT_19','BPED_15','BPharm_2008','BPharm_2013','BPharm_2015','BPharm_2018','BPharm_2019','BSC_19','BSC_ANIMATION_21','BSC_BIO_19','BSC_C_DS_22','BSC_CS_19','BSC_HS_19','CCINFMJ','DCCL','DCIPRL','Dev_Course','DIBF_Com','DIIB_Com','DLLLW','DTL','LLB_17','LLM_14','M_Pharm_19','MA_23','MA_MJMC_19','MA_MSc_Geograpgy_23','MA_MSc_Statistics_23','MA_MScStat_2018','MA_MscStat_2019','MA_Political_Science_23','MA_Test_2023','MBA_19','MBA_Digital_Marketing_21','MBA_FinTech_21','MBA_HRD_20','MBA_IT_20','MBA_Project_Mgt_21','MBA_Service_Mgt_21','MCA_ENGG_20','MCA_MGT_20','MCA_MGT_24','MCom_23','ME_2013','ME_2017','MED_16','MSc_Analytical_Chemistry_23','MSc_Bio_Chemistry_23','MSc_Biotechnology_23','MSc_Botany_23','MSc_CA_23','MSc_CS_23','MSc_Drug_Chemistry_23','MSc_Electronics_23','MSc_Environmental_Science_23','MSc_Inorganic_Chemistry_23','MSc_IT_23','MSc_Mathematics_23','MSc_Microbiology_23','MSc_Organic_Chemistry_23','MSc_Physical_Chemistry_23','MSc_Physics_23','MSc_Tech_Mtech_23','MSc_Zoology_23','PG_DIT_Com','PGDCM_22','PGDHM_19','DPharmacy_2019','MSc_Statistics_24','MSc_Zoology_24','BSC_CS_2024','BAToBA_19','BPED_10Point_15','SODL_MBA_21','Test_2015') order by name""") 
databases = [row[0] for row in cursor.fetchall()] 
 
print("Databases found:") 
for db in databases: 
    print(db) 
 
query=""";WITH YearPartCount AS 
( 
    SELECT 
        YearId, 
        COUNT(DISTINCT YearPartId) AS YearPartCount 
    FROM dbo.YearPart 
    GROUP BY YearId 
), 
SysParaData AS 
( 
    SELECT DISTINCT 
        ExamCode, 
        ResultType 
    FROM dbo.syspara 
) 
 
INSERT INTO [BArch_2015].[dbo].[StudentApi] 
( 
    [SeatNo], 
    [PRN], 
    [Name], 
    [MotherName], 
    [PassingYear], 
    [PassingMonth], 
    [ResultStatus], 
    [Course_id], 
    [pattern], 
    [semyear], 
    [CourseType], 
    [Specialization] 
) 
 
SELECT 
    b.SeatNo, 
    c.UID, 
    c.FullName, 
    c.MotherName, 
 
    YEAR(q.ExamPeriod) AS PassingYear, 
    MONTH(q.ExamPeriod) AS PassingMonth, 
 
    CASE 
        WHEN (b.ResultId & 8) = 8 THEN 'Pass' 
        WHEN (b.ResultId & 2) = 2 THEN 'Fail' 
        WHEN (b.ResultId & 4) = 4 THEN 'Fail_ATKT' 
        WHEN (b.ResultId & 1) = 1 THEN 'Reserve' 
    END AS ResultStatus, 
 
    z.ExamCode AS Course_id, 
 
    CASE 
        WHEN yp.YearPartCount = 1 
            THEN 'Annual' 
        ELSE 'Semester' 
    END AS pattern, 
 
    CASE 
        WHEN yp.YearPartCount = 1 
            THEN 'Year ' + CONVERT(VARCHAR(2), p.YearPartId) 
        ELSE 
            'Semester ' + CONVERT(VARCHAR(2), p.YearPartId) 
    END AS semyear, 
 
    CASE 
        WHEN z.ResultType = 3 
            THEN 'School of Open learning' 
        ELSE 'Regular' 
    END AS CourseType, 
 
    '' AS Specialization 
 
FROM dbo.ExamForm a 
 
INNER JOIN dbo.ExamFormResult b 
    ON b.ExamFormId = a.ExamFormId 
 
INNER JOIN dbo.Student c 
    ON c.StudentId = a.StudentId 
 
INNER JOIN dbo.Branch y 
    ON y.BranchId = c.BranchId 
 
INNER JOIN dbo.Period q 
    ON q.PeriodId = a.PeriodId 
 
INNER JOIN dbo.ResultClass i 
    ON i.ClassId = b.ClassId 
 
INNER JOIN YearPartCount yp 
    ON yp.YearId = b.YearId 
 
CROSS APPLY 
( 
    SELECT TOP (1) 
        X.YearPartId 
    FROM dbo.Performance m 
 
    INNER JOIN dbo.PaperAssHd n 
        ON n.PaperAssHdId = m.PaperAssHdId 
 
    INNER JOIN dbo.Paper v 
        ON v.PaperId = n.PaperId 
 
    INNER JOIN dbo.YearPart X 
        ON X.YearPartId = v.YearPartId 
 
    WHERE m.StudentId = c.StudentId 
      AND m.PeriodId <= a.PeriodId 
 
    ORDER BY X.YearPartId DESC 
) p 
 
CROSS JOIN SysParaData z 
 
WHERE b.SeatNo > '0' 
  AND b.YearId > 0; """ 
 
for db in databases: 
    print(f"\nExecuting in:{db}") 
    try: 
        cursor.execute(f"USE [{db}];") 
        cursor.execute(query) 
        conn.commit() 
        print(f"Data inserted successfully in {db}.") 
    except Exception as e: 
        print(f"Error in {db}: {e}") 
conn.close() 
 
print("===================server 2=======================") 
conn = mssql_python.connect( 
    f"Server={server2};" 
    f"Database=master;" 
    f"UID=importer;" 
    f"PWD=importer;" 
    "TrustServerCertificate=yes;" 
) 
cursor = conn.cursor() 
 
cursor.execute(""" SELECT name FROM master.sys.DATABASES WITH(NOLOCK) WHERE state=0 and name not IN ('master','tempdb','model','msdb') order by name""") 
databases = [row[0] for row in cursor.fetchall()] 
 
print("Databases found:") 
for db in databases: 
    print(db) 
 
query=""";WITH YearPartCount AS 
( 
    SELECT 
        YearId, 
        COUNT(DISTINCT YearPartId) AS YearPartCount 
    FROM dbo.YearPart 
    GROUP BY YearId 
), 
SysParaData AS 
( 
    SELECT DISTINCT 
        ExamCode, 
        ResultType 
    FROM dbo.syspara 
) 
 
INSERT INTO [ResultMaster].[dbo].[StudentApi] 
( 
    [SeatNo], 
    [PRN], 
    [Name], 
    [MotherName], 
    [PassingYear], 
    [PassingMonth], 
    [ResultStatus], 
    [Course_id], 
    [pattern], 
    [semyear], 
    [CourseType], 
    [Specialization] 
) 
 
SELECT 
    b.SeatNo, 
    c.UID, 
    c.FullName, 
    c.MotherName, 
 
    YEAR(q.ExamPeriod) AS PassingYear, 
    MONTH(q.ExamPeriod) AS PassingMonth, 
 
    CASE 
        WHEN (b.ResultId & 8) = 8 THEN 'Pass' 
        WHEN (b.ResultId & 2) = 2 THEN 'Fail' 
        WHEN (b.ResultId & 4) = 4 THEN 'Fail_ATKT' 
        WHEN (b.ResultId & 1) = 1 THEN 'Reserve' 
    END AS ResultStatus, 
 
    z.ExamCode AS Course_id, 
 
    CASE 
        WHEN yp.YearPartCount = 1 
            THEN 'Annual' 
        ELSE 'Semester' 
    END AS pattern, 
 
    CASE 
        WHEN yp.YearPartCount = 1 
            THEN 'Year ' + CONVERT(VARCHAR(2), p.YearPartId) 
        ELSE 
            'Semester ' + CONVERT(VARCHAR(2), p.YearPartId) 
    END AS semyear, 
 
    CASE 
        WHEN z.ResultType = 3 
            THEN 'School of Open learning' 
        ELSE 'Regular' 
    END AS CourseType, 
 
    '' AS Specialization 
 
FROM dbo.ExamForm a 
 
INNER JOIN dbo.ExamFormResult b 
    ON b.ExamFormId = a.ExamFormId 
 
INNER JOIN dbo.Student c 
    ON c.StudentId = a.StudentId 
 
INNER JOIN dbo.Branch y 
    ON y.BranchId = c.BranchId 
 
INNER JOIN dbo.Period q 
    ON q.PeriodId = a.PeriodId 
 
INNER JOIN dbo.ResultClass i 
    ON i.ClassId = b.ClassId 
 
INNER JOIN YearPartCount yp 
    ON yp.YearId = b.YearId 
 
CROSS APPLY 
( 
    SELECT TOP (1) 
        X.YearPartId 
    FROM dbo.Performance m 
 
    INNER JOIN dbo.PaperAssHd n 
        ON n.PaperAssHdId = m.PaperAssHdId 
 
    INNER JOIN dbo.Paper v 
        ON v.PaperId = n.PaperId 
 
    INNER JOIN dbo.YearPart X 
        ON X.YearPartId = v.YearPartId 
 
    WHERE m.StudentId = c.StudentId 
      AND m.PeriodId <= a.PeriodId 
 
    ORDER BY X.YearPartId DESC 
) p 
 
CROSS JOIN SysParaData z 
 
WHERE b.SeatNo > '0' 
  AND b.YearId > 0; """ 
 
for db in databases: 
    print(f"\nExecuting in:{db}") 
    try: 
        cursor.execute(f"USE [{db}];") 
        cursor.execute(query) 
        conn.commit() 
        print(f"Data inserted successfully in {db}.") 
    except Exception as e: 
        print(f"Error in {db}: {e}") 
conn.close() 
print("===================server 3=======================") 
 
conn = mssql_python.connect( 
    f"Server={server3};" 
    f"Database=master;" 
    f"UID=importer;" 
    f"PWD=importer;" 
    "TrustServerCertificate=yes;" 
) 
cursor = conn.cursor() 
 
cursor.execute(""" SELECT nameFROM master.sys.DATABASES WITH(NOLOCK) WHERE state=0 and (name in ('BA_19','FE_2024','BSC_24','FE_24','H_BALLB_17','H_BA_19','H_BBA_19','H_BBA_CA_19','H_BBA_IB_19','H_BCASci_19','H_BCom_19','H_Bsc_19','H_Bsc_Cyber_Digital_22','H_BScAni_21','H_BscBio_19','H_BscCs_19','H_BscHs_19','H_CCINFMJ','H_DCCL','H_DCIPRL','H_DLLLW','H_DTL_18','H_LLB_17','H_LLB_19','H_LLM_14','H_M.scCompSci_19','H_M.Tech_19','H_MA_19','H_Mcom_19','H_Msc_19','H_BHMCT_19','H_Msc_Biochem_19','H_MscAnalyticalChem_19','H_MscBiotechnology_19','H_MscBotany_19','H_MscCA_20','H_MscDrugChem_19','H_MscElectronics_19','H_MscEnviSci_19','H_MscGeography_19','H_MscInorganicChem_19','H_MscMath_19','H_MscMicrobiology_19','H_MscOrganicChem_19','H_MscPhysChemistry_19','H_MscPhysics_20','H_MscStat_19','H_MscZoo_19','H_PGDIBF_20','H_PGDIIB','H_PGDIT','Hybrid_MA_23','Hybrid_MCom_23','Hybrid_MSc_Analytical_Chemistry_23','Hybrid_MSc_BIOTECHNOLOGY_23','Hybrid_MSc_BOTANY_23','Hybrid_MSc_CA_23','Hybrid_MSc_CS_23','Hybrid_MSc_Drug_Chemistry_23','Hybrid_MSc_ELECTRONICS_23','Hybrid_MSc_ENV_SCIENCE_23','Hybrid_MSc_GEOGRAPHY_23','Hybrid_MSc_Inorganic_Chemistry_23','Hybrid_MSc_MATHEMATICS_23','Hybrid_MSc_Microbiology_23','Hybrid_MSc_Organic_Chemistry_23','Hybrid_MSc_PHY_CHEMISTRY_23','Hybrid_MSc_PHYSICS_23','Hybrid_MSc_Zoology_24','TE_19','MCA_ENGG_25','SE_24','ME_25','H_MCA_ENGG_20','H_MBA_IT_20','H_MCA_mgnt_20','H_MBA_HRD_20','H_MBA_SM_21','H_MBA_DM_21','H_MBA_19','H_BPED_15','BArch_25','BscToBsc_19','H_MED_16','H_BED_15','MED_25','BED_25','BHMCT_25','Mcom_25','MSc_Zoology_25') or database_id>116) order by name""") 
databases = [row[0] for row in cursor.fetchall()] 
 
print("Databases found:") 
for db in databases: 
    print(db) 
 
query=""";WITH YearPartCount AS 
( 
    SELECT 
        YearId, 
        COUNT(DISTINCT YearPartId) AS YearPartCount 
    FROM dbo.YearPart 
    GROUP BY YearId 
), 
SysParaData AS 
( 
    SELECT DISTINCT 
        ExamCode, 
        ResultType 
    FROM dbo.syspara 
) 
 
INSERT INTO [ResultHistory].[dbo].[StudentApi] 
( 
    [SeatNo], 
    [PRN], 
    [Name], 
    [MotherName], 
    [PassingYear], 
    [PassingMonth], 
    [ResultStatus], 
    [Course_id], 
    [pattern], 
    [semyear], 
    [CourseType], 
    [Specialization] 
) 
 
SELECT 
    b.SeatNo, 
    c.UID, 
    c.FullName, 
    c.MotherName, 
 
    YEAR(q.ExamPeriod) AS PassingYear, 
    MONTH(q.ExamPeriod) AS PassingMonth, 
 
    CASE 
        WHEN (b.ResultId & 8) = 8 THEN 'Pass' 
        WHEN (b.ResultId & 2) = 2 THEN 'Fail' 
        WHEN (b.ResultId & 4) = 4 THEN 'Fail_ATKT' 
        WHEN (b.ResultId & 1) = 1 THEN 'Reserve' 
    END AS ResultStatus, 
 
    z.ExamCode AS Course_id, 
 
    CASE 
        WHEN yp.YearPartCount = 1 
            THEN 'Annual' 
        ELSE 'Semester' 
    END AS pattern, 
 
    CASE 
        WHEN yp.YearPartCount = 1 
            THEN 'Year ' + CONVERT(VARCHAR(2), p.YearPartId) 
        ELSE 
            'Semester ' + CONVERT(VARCHAR(2), p.YearPartId) 
    END AS semyear, 
 
    CASE 
        WHEN z.ResultType = 3 
            THEN 'School of Open learning' 
        ELSE 'Regular' 
    END AS CourseType, 
 
    '' AS Specialization 
 
FROM dbo.ExamForm a 
 
INNER JOIN dbo.ExamFormResult b 
    ON b.ExamFormId = a.ExamFormId 
 
INNER JOIN dbo.Student c 
    ON c.StudentId = a.StudentId 
 
INNER JOIN dbo.Branch y 
    ON y.BranchId = c.BranchId 
 
INNER JOIN dbo.Period q 
    ON q.PeriodId = a.PeriodId 
 
INNER JOIN dbo.ResultClass i 
    ON i.ClassId = b.ClassId 
 
INNER JOIN YearPartCount yp 
    ON yp.YearId = b.YearId 
 
CROSS APPLY 
( 
    SELECT TOP (1) 
        X.YearPartId 
    FROM dbo.Performance m 
 
    INNER JOIN dbo.PaperAssHd n 
        ON n.PaperAssHdId = m.PaperAssHdId 
 
    INNER JOIN dbo.Paper v 
        ON v.PaperId = n.PaperId 
 
    INNER JOIN dbo.YearPart X 
        ON X.YearPartId = v.YearPartId 
 
    WHERE m.StudentId = c.StudentId 
      AND m.PeriodId <= a.PeriodId 
 
    ORDER BY X.YearPartId DESC 
) p 
 
CROSS JOIN SysParaData z 
 
WHERE b.SeatNo > '0' 
  AND b.YearId > 0; """ 
 
for db in databases: 
    print(f"\nExecuting in:{db}") 
    try: 
        cursor.execute(f"USE [{db}];") 
        cursor.execute(query) 
        conn.commit() 
        print(f"Data inserted successfully in {db}.") 
    except Exception as e: 
        print(f"Error in {db}: {e}") 
conn.close() 
it is taking more than half hour and still continue
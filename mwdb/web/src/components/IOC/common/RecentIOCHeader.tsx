export function RecentIOCHeader() {
    return (
        <>
            <th className="col-lg-5 col-6">
                <span className="d-lg-none">IOC Info</span>
                <span className="d-none d-lg-inline">Type / Value</span>
            </th>
            <th className="col-lg-3 col-6">
                <span className="d-lg-none">Details</span>
                <span className="d-none d-lg-inline">Severity / Status / Source</span>
            </th>
            <th className="col-lg-4 col-12 d-none d-lg-table-cell">Tags</th>
        </>
    );
}

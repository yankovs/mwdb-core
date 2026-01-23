import { RecentView } from "@mwdb-web/components/RecentView";
import { RecentIOCRow } from "../common/RecentIOCRow";
import { RecentIOCHeader } from "../common/RecentIOCHeader";

export function RecentIOCsView() {
    return (
        <RecentView
            type="ioc"
            rowComponent={RecentIOCRow}
            headerComponent={RecentIOCHeader}
        />
    );
}

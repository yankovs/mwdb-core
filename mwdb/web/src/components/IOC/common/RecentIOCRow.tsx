import { TagList } from "@mwdb-web/commons/ui";
import { DateString, ObjectLink } from "@mwdb-web/commons/ui";
import { RecentInnerRow, RecentRow } from "@mwdb-web/components/RecentView";
import { RecentRowProps } from "@mwdb-web/types/props";
import { IOCListItem } from "@mwdb-web/types/types";
import { IOCTypeBadge, IOCSeverityBadge } from "../IOCComponents";

export function RecentIOCRow(props: RecentRowProps<IOCListItem>) {
    const uploadTime = <DateString date={props.upload_time} />;
    const tags = (
        <TagList
            tag=""
            tags={props.tags}
            tagClick={(ev, tag) => {
                ev.preventDefault();
                props.addToQuery("tag", tag);
            }}
            tagRemove={(ev, tag) => props.addToQuery("NOT tag", tag)}
            filterable
        />
    );

    const typeBadge = <IOCTypeBadge type={props.ioc_type} />;
    const severityBadge = <IOCSeverityBadge severity={props.severity} />;
    const statusBadge = props.is_active ? (
        <span className="badge badge-success">Active</span>
    ) : (
        <span className="badge badge-secondary">Inactive</span>
    );

    return (
        <RecentRow firstSeen={props.upload_time}>
            <>
                <td className="col-lg-5 col-6">
                    {/* Wide mode */}
                    <RecentInnerRow
                        labelWidth="5rem"
                        label="Type"
                        wideOnly
                        noEllipsis
                    >
                        {typeBadge}
                    </RecentInnerRow>
                    <RecentInnerRow
                        labelWidth="5rem"
                        label="Value"
                        value={props.value}
                        wideOnly
                        copyable
                    >
                        <ObjectLink type="ioc" id={props.id} />
                    </RecentInnerRow>
                    {/* Shrinked mode */}
                    <RecentInnerRow noEllipsis narrowOnly>
                        {typeBadge}
                    </RecentInnerRow>
                    <RecentInnerRow value={props.value} narrowOnly copyable>
                        <ObjectLink type="ioc" id={props.id} />
                    </RecentInnerRow>
                    <RecentInnerRow
                        value={props.upload_time}
                        narrowOnly
                        noEllipsis
                    >
                        {uploadTime}
                    </RecentInnerRow>
                </td>
                <td className="col-lg-3 col-6">
                    {/* All modes */}
                    <RecentInnerRow
                        labelWidth="4.5rem"
                        label="Severity"
                        noEllipsis
                    >
                        {severityBadge}
                    </RecentInnerRow>
                    <RecentInnerRow
                        labelWidth="4.5rem"
                        label="Status"
                        noEllipsis
                    >
                        {statusBadge}
                    </RecentInnerRow>
                    {props.source && (
                        <RecentInnerRow
                            labelWidth="4.5rem"
                            label="Source"
                            value={props.source}
                            copyable
                        />
                    )}
                    {/* Shrink mode */}
                    <RecentInnerRow narrowOnly noEllipsis>
                        {tags}
                    </RecentInnerRow>
                </td>
                <td className="col-lg-4 col-12 d-none d-lg-flex">
                    {/* Wide mode only */}
                    <RecentInnerRow
                        labelWidth="3rem"
                        label="Tags"
                        noEllipsis
                    >
                        {tags}
                    </RecentInnerRow>
                </td>
            </>
        </RecentRow>
    );
}

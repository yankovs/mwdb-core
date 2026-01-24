import { useContext, useEffect, useState } from "react";
import { toast } from "react-toastify";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faPlus } from "@fortawesome/free-solid-svg-icons";
import { APIContext } from "@mwdb-web/commons/api";
import { ObjectContext } from "@mwdb-web/commons/context";
import { ObjectTab } from "@mwdb-web/commons/ui";
import { faVial } from "@fortawesome/free-solid-svg-icons";
import { IOCTypeBadge, IOCSeverityBadge } from "@mwdb-web/components/IOC";
import { ObjectLink } from "@mwdb-web/commons/ui";
import { RelatedObject } from "@mwdb-web/types/types";
import { IOCAddModal } from "../Actions/IOCAddModal";
import { getErrorMessage } from "@mwdb-web/commons/helpers";

type IOCGroup = {
    [key: string]: RelatedObject[];
};

export function IOCTab() {
    const api = useContext(APIContext);
    const context = useContext(ObjectContext);
    const [immediateIOCs, setImmediateIOCs] = useState<IOCGroup>({});
    const [transitiveIOCs, setTransitiveIOCs] = useState<IOCGroup>({});
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [isIOCAddModalOpen, setIOCAddModalOpen] = useState<boolean>(false);

    useEffect(() => {
        const loadIOCs = async () => {
            if (!context.object?.id) return;

            try {
                setLoading(true);
                setError(null);

                // Fetch all relations
                const response = await api.getObjectRelations(context.object.id!);
                const allRelations = [
                    ...response.data.parents,
                    ...response.data.children,
                ];

                // Filter for IOC objects
                const iocRelations = allRelations.filter(
                    (rel) => rel.type === "ioc"
                );

                // Group IOCs by type
                const immediateByType: IOCGroup = {};
                iocRelations.forEach((ioc) => {
                    const iocType = ioc.type || "unknown";
                    if (!immediateByType[iocType]) {
                        immediateByType[iocType] = [];
                    }
                    immediateByType[iocType].push(ioc);
                });

                setImmediateIOCs(immediateByType);

                // For transitive IOCs, fetch children and their IOCs
                const transitiveByType: IOCGroup = {};

                for (const child of response.data.children) {
                    if (child.type === "ioc") continue; // Skip direct IOCs

                    try {
                        const childRelations = await api.getObjectRelations(child.id);

                        const childIOCs = [
                            ...childRelations.data.parents,
                            ...childRelations.data.children,
                        ].filter((rel) => rel.type === "ioc");

                        childIOCs.forEach((ioc) => {
                            const iocType = ioc.type || "unknown";
                            if (!transitiveByType[iocType]) {
                                transitiveByType[iocType] = [];
                            }
                            // Avoid duplicates
                            if (
                                !transitiveByType[iocType].some(
                                    (existing) => existing.id === ioc.id
                                )
                            ) {
                                transitiveByType[iocType].push(ioc);
                            }
                        });
                    } catch (err) {
                        // Silently skip errors for individual child relations
                    }
                }

                setTransitiveIOCs(transitiveByType);
            } catch (err) {
                setError("Failed to load related IOCs");
                console.error("Error loading IOCs:", err);
            } finally {
                setLoading(false);
            }
        };

        loadIOCs();
    }, [context.object?.id, api]);

    const refreshIOCList = async () => {
        if (!context.object?.id) return;

        try {
            setError(null);

            // Fetch all relations
            const response = await api.getObjectRelations(context.object.id!);
            const allRelations = [
                ...response.data.parents,
                ...response.data.children,
            ];

            // Filter for IOC objects
            const iocRelations = allRelations.filter(
                (rel) => rel.type === "ioc"
            );

            // Group IOCs by type
            const immediateByType: IOCGroup = {};
            iocRelations.forEach((ioc) => {
                const iocType = ioc.type || "unknown";
                if (!immediateByType[iocType]) {
                    immediateByType[iocType] = [];
                }
                immediateByType[iocType].push(ioc);
            });

            setImmediateIOCs(immediateByType);

            // For transitive IOCs, fetch children and their IOCs
            const transitiveByType: IOCGroup = {};

            for (const child of response.data.children) {
                if (child.type === "ioc") continue; // Skip direct IOCs

                try {
                    const childRelations = await api.getObjectRelations(child.id);

                    const childIOCs = [
                        ...childRelations.data.parents,
                        ...childRelations.data.children,
                    ].filter((rel) => rel.type === "ioc");

                    childIOCs.forEach((ioc) => {
                        const iocType = ioc.type || "unknown";
                        if (!transitiveByType[iocType]) {
                            transitiveByType[iocType] = [];
                        }
                        // Avoid duplicates
                        if (
                            !transitiveByType[iocType].some(
                                (existing) => existing.id === ioc.id
                            )
                        ) {
                            transitiveByType[iocType].push(ioc);
                        }
                    });
                } catch (err) {
                    // Silently skip errors for individual child relations
                }
            }

            setTransitiveIOCs(transitiveByType);
        } catch (err) {
            setError("Failed to refresh IOCs");
            console.error("Error refreshing IOCs:", err);
        }
    };

    const handleAddIOC = async (ioc_type: string, value: string) => {
        if (!context.object?.id) return;

        try {
            // Create the IOC
            const createResponse = await api.createIOC(
                ioc_type,
                value,
                undefined,
                undefined,
                true,
                undefined,
                undefined,
                false
            );

            // Add relation between the current object and the IOC
            const iocId = createResponse.data.id;
            await api.addObjectRelation(context.object.id, iocId);

            // Close modal and refresh the IOCs list
            setIOCAddModalOpen(false);
            await refreshIOCList();
            toast("IOC added successfully", { type: "success" });
        } catch (err: any) {
            const errorMessage = getErrorMessage(err);
            toast(errorMessage, { type: "error" });
            console.error("Error adding IOC:", err);
        }
    };

    const renderIOCGroup = (iocsMap: IOCGroup, title: string) => {
        const hasIOCs = Object.keys(iocsMap).length > 0;

        if (!hasIOCs) {
            return (
                <div className="mt-3">
                    <h6>{title}</h6>
                    <p className="text-muted">No {title.toLowerCase()}</p>
                </div>
            );
        }

        return (
            <div className="mt-3">
                <h6>{title}</h6>
                {Object.entries(iocsMap).map(([iocType, iocs]) => (
                    <div key={iocType} className="mb-3">
                        <div className="font-weight-bold mb-2">
                            <span className="badge badge-info">{iocType}</span>
                            <span className="ml-2 text-muted">
                                ({iocs.length})
                            </span>
                        </div>
                        <div className="list-group">
                            {iocs.map((ioc) => (
                                <div
                                    key={ioc.id}
                                    className="list-group-item list-group-item-action p-2"
                                >
                                    <div className="d-flex justify-content-between align-items-start">
                                        <div className="flex-grow-1">
                                            <ObjectLink
                                                type={ioc.type}
                                                id={ioc.id}
                                            />
                                        </div>
                                        <div className="ml-2">
                                            {ioc.tags && ioc.tags.length > 0 && (
                                                <div className="d-flex flex-wrap gap-1 justify-content-end">
                                                    {ioc.tags.map((tag) => (
                                                        <span
                                                            key={tag.tag}
                                                            className="badge badge-secondary"
                                                        >
                                                            {tag.tag}
                                                        </span>
                                                    ))}
                                                </div>
                                            )}
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                ))}
            </div>
        );
    };

    return (
        <>
            <IOCAddModal
                isOpen={isIOCAddModalOpen}
                onRequestModalClose={() => setIOCAddModalOpen(false)}
                onSubmit={handleAddIOC}
            />
            <ObjectTab
                tab="iocs"
                icon={faVial}
                dropdownActions={false}
                component={() => (
                    <div className="card-body">
                        <div className="mb-3">
                            <button
                                className="btn btn-sm btn-primary"
                                onClick={() => setIOCAddModalOpen(true)}
                                title="Add IOC"
                            >
                                <FontAwesomeIcon icon={faPlus} /> Add IOC
                            </button>
                        </div>
                        {loading && (
                            <div className="text-center">
                                <div className="spinner-border" role="status">
                                    <span className="sr-only">Loading...</span>
                                </div>
                            </div>
                        )}
                        {error && (
                            <div className="alert alert-danger" role="alert">
                                {error}
                            </div>
                        )}
                        {!loading && !error && (
                            <>
                                {renderIOCGroup(immediateIOCs, "Direct IOCs")}
                                {Object.keys(transitiveIOCs).length > 0 && (
                                    renderIOCGroup(
                                        transitiveIOCs,
                                        "IOCs from Related Objects"
                                    )
                                )}
                                {Object.keys(immediateIOCs).length === 0 &&
                                    Object.keys(transitiveIOCs).length === 0 && (
                                        <p className="text-muted">
                                            No related IOCs found
                                        </p>
                                    )}
                            </>
                        )}
                    </div>
                )}
            />
        </>
    );
}

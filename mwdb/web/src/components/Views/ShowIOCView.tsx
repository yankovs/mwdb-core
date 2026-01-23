import { useContext } from "react";
import { useParams } from "react-router-dom";
import { APIContext } from "@mwdb-web/commons/api";
import { useRemotePath } from "@mwdb-web/commons/remotes";
import {
    ShowObject,
    ObjectTab,
    RelationsTab,
    FavoriteAction,
    PushAction,
    PullAction,
    RemoveAction,
} from "../ShowObject";
import { faVial, faSearch } from "@fortawesome/free-solid-svg-icons";
import { IOCDetailComponent } from "@mwdb-web/components/IOC";
import { Extendable } from "@mwdb-web/commons/plugins";

export function ShowIOCView() {
    const api = useContext(APIContext);
    const params = useParams();
    const remotePath = useRemotePath();

    return (
        <ShowObject
            ident="showIOC"
            objectType="ioc"
            objectId={params.hash ?? ""}
            searchEndpoint={`${remotePath}/`}
            headerIcon={faVial}
            headerCaption="IOC details"
        >
            <Extendable ident="iocTabs">
                <ObjectTab
                    tab="details"
                    icon={faVial}
                    component={IOCDetailComponent}
                    actions={[
                        <FavoriteAction />,
                        <PullAction />,
                        <PushAction />,
                        <RemoveAction />,
                    ]}
                />
                <RelationsTab />
            </Extendable>
        </ShowObject>
    );
}

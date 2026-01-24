import * as Yup from "yup";
import { ConfirmationModal, FormError, Label } from "@mwdb-web/commons/ui";
import { UseFormProps, useForm } from "react-hook-form";
import { yupResolver } from "@hookform/resolvers/yup";

type FormValues = {
    ioc_type: string;
    value: string;
};

const validationSchema: Yup.SchemaOf<FormValues> = Yup.object().shape({
    ioc_type: Yup.string().required("Please select an IOC type."),
    value: Yup.string().required("IOC value is required"),
});

const formOptions: UseFormProps<FormValues> = {
    resolver: yupResolver(validationSchema),
    mode: "onSubmit",
    reValidateMode: "onSubmit",
    shouldFocusError: true,
    defaultValues: {
        ioc_type: "",
        value: "",
    },
};

type Props = {
    isOpen: boolean;
    onSubmit: (ioc_type: string, value: string) => void;
    onRequestModalClose: () => void;
};

export function IOCAddModal(props: Props) {
    const {
        register,
        reset,
        handleSubmit,
        formState: { errors },
    } = useForm<FormValues>(formOptions);

    function handleClose() {
        reset();
        props.onRequestModalClose();
    }

    function createIOC(values: FormValues) {
        props.onSubmit(values.ioc_type, values.value);
    }

    return (
        <ConfirmationModal
            buttonStyle="btn-success"
            confirmText="Add"
            message="Add IOC"
            isOpen={props.isOpen}
            onRequestClose={handleClose}
            onConfirm={() => handleSubmit(createIOC)()}
        >
            <div className="form-group">
                <Label
                    label="IOC Type"
                    required
                    htmlFor={"ioc_type" as keyof FormValues}
                />
                <select
                    {...register("ioc_type" as keyof FormValues)}
                    id={"ioc_type" as keyof FormValues}
                    className={`form-control ${
                        errors.ioc_type ? "is-invalid" : ""
                    }`.trim()}
                    style={{ width: 200 }}
                >
                    <option value="" hidden>
                        Select IOC type
                    </option>
                    <option value="ip">IP Address</option>
                    <option value="domain">Domain</option>
                    <option value="url">URL</option>
                    <option value="hash">Hash</option>
                    <option value="email">Email</option>
                    <option value="filename">Filename</option>
                    <option value="registry">Registry Key</option>
                    <option value="process">Process</option>
                </select>
                <FormError errorField={errors.ioc_type} />
            </div>
            <div className="form-group">
                <Label
                    label="Value"
                    required
                    htmlFor={"value" as keyof FormValues}
                />
                <input
                    {...register("value" as keyof FormValues)}
                    id={"value" as keyof FormValues}
                    className={`form-control ${
                        errors.value ? "is-invalid" : ""
                    }`.trim()}
                    style={{ width: 600 }}
                    placeholder="Enter IOC value"
                />
                <FormError errorField={errors.value} />
            </div>
        </ConfirmationModal>
    );
}

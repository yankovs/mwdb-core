import { capitalize, intersperse, mapObjectType } from "../../commons/helpers";

describe("capitalize", () => {
    test("should return empty string when param is not typeof string", () => {
        const string = {};
        const expected = "";
        const result = capitalize(string);
        expect(result).toEqual(expected);
    });

    test("should return capitalize first letter of string", () => {
        const string = "tom";
        const expected = "Tom";
        const result = capitalize(string);
        expect(result).toEqual(expected);
    });

    test("should return the same string if first letter is already capitalize", () => {
        const string = "John";
        const expected = "John";
        const result = capitalize(string);
        expect(result).toEqual(expected);
    });
});

describe("intersperse", () => {
    test("should return an empty array when passed an empty array", () => {
        const expected = [];
        const result = intersperse([], "-");
        expect(result).toEqual(expected);
    });

    it("should intersperse a single item in an array", () => {
        const expected = [1, "-", 2, "-", 3];
        const result = intersperse([1, 2, 3], "-");
        expect(result).toEqual(expected);
    });

    it("should intersperse multiple items in an array", () => {
        const expected = [1, "-", ".", 2, "-", ".", 3];
        const result = intersperse([1, 2, 3], ["-", "."]);
        expect(expected).toEqual(result);
    });
});

describe("mapObjectType", () => {
    it("should return 'object' when passed 'object'", () => {
        const result = mapObjectType("object");
        expect(result).toBe("object");
    });

    it("should return 'file' when passed 'file'", () => {
        const result = mapObjectType("file");
        expect(result).toBe("file");
    });

    it("should return 'config' when passed 'static_config'", () => {
        const result = mapObjectType("static_config");
        expect(result).toBe("config");
    });

    it("should return 'blob' when passed 'text_blob'", () => {
        const result = mapObjectType("text_blob");
        expect(result).toBe("blob");
    });

    it("should return the input string if it does not match any of the predefined values", () => {
        const result = mapObjectType("unknown");
        expect(result).toBe("unknown");
    });
});
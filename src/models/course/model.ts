import { mongoose } from "../../config/database";

interface course_interface extends mongoose.Document {
    code: String;
    conventional_code: String;
    name: String;
    semester: String;
    department: String;
    faculty: {
        professors: {
            name: String;
            email: String;
        };
        TFs: {
            name: String;
            email: String;
        };
    };
    document: String;
    html_details: String;
    ratings: {
        sample_size: Number;
        engaging: Number;
        interesting_material: Number;
        grading: Number;
        workload: Number;
        attendance: Number;
        TFs: Number;
        holistic: Number;
        compound_score: Number;
    };
}

const course_schema = new mongoose.Schema(
    {
        code: [{ type: String, default: "" }],
        conventional_code: { type: String, default: "" },
        name: { type: String, default: "" },
        semester: { type: String, default: "" },
        department: { type: String, default: "" },
        faculty: {
            professors: [
                {
                    name: { type: String, default: "" },
                    email: { type: String, default: "" },
                },
            ],
            TFs: [
                {
                    name: { type: String, default: "" },
                    email: { type: String, default: "" },
                },
            ],
        },
        document: { type: String, default: "" },
        html_details: { type: String, default: "" },
        ratings: {
            sample_size: { type: Number, default: 0 },
            engaging: { type: Number, default: 0 },
            interesting_material: { type: Number, default: 0 },
            grading: { type: Number, default: 0 },
            workload: { type: Number, default: 0 },
            attendance: { type: Number, default: 0 },
            TFs: { type: Number, default: 0 },
            holistic: { type: Number, default: 0 },
            compound_score: { type: Number, default: 0 },
        },
    },
    {
        collection: "courses",
    }
);

export const Course = mongoose.model<course_interface>("Course", course_schema);

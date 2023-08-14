// connect to mongodb through mongosh :
// mongodb://localhost:27017/db

// query mongodb to list all databases
db.adminCommand("listDatabases");

// inspect a single document
db.my_collection.find().pretty();

// aggregation pipeline
// count the distinct occurences for each tag (tag appears in an array)
db.my_collection.aggregate([
  { $unwind: "$tags" },
  { $group: { _id: "$tags", count: { $sum: 1 } } },
  { $sort: { count: -1 } },
  { $project: { _id: 0, tag: "$_id", count: 1 } },
]);

// find the title of the document with the highest number of tags
db.my_collection
  .find({}, { title: 1, tags: 1, _id: 0 })
  .sort({ tags: -1 })
  .limit(1);

// aggregation pipeline matching documents with "regressions" in the pile field
// then unwind pile and tags field
// then group by pile and count the number of documents in total that have a certain tag
db.my_collection.aggregate([
  { $match: { pile: "regressions" } },
  { $unwind: "$pile" },
  { $unwind: "$tags" },
  { $group: { _id: "$pile", count: { $sum: 1 } } },
]);

// aggregation pipeline
// then unwind pile and tags field
// then group by pile and tags
// and count the number of documents
// that have a certain pile, tag combo
// then sort by count descending
// then project only pile, tag and count, hide the id
db.my_collection.aggregate([
  { $unwind: "$pile" },
  { $unwind: "$tags" },
  { $group: { _id: { pile: "$pile", tag: "$tags" }, count: { $sum: 1 } } },
  { $sort: { count: -1 } },
  { $project: { _id: 0, pile: "$_id.pile", tag: "$_id.tag", count: 1 } },
]);

// find the tenure for each document
// given the a publication date
// tenure is the number of days the article is has been available
// publication_date is currently stored as a string
// so we need to convert it to a date
// then we can use the $subtract operator to find the difference
// between the current date and the publication date. that is the tenure
db.my_collection.aggregate([
  { $project: { _id: 0, title: 1, publication_date: 1 } },
  { $addFields: { publication_date: { $toDate: "$publication_date" } } },
  { $addFields: { tenure: { $subtract: [new Date(), "$publication_date"] } } },
  { $project: { title: 1, tenure: 1 } },
]);

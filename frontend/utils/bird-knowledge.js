const BIRD_KNOWLEDGE = [
  {
    id: 1,
    commonName: "Common Kingfisher",
    chineseName: "普通翠鸟",
    scientificName: "Alcedo atthis",
    confidenceStatus: "Least Concern",
    bio: "体型小巧，头背呈亮蓝色，腹部橙褐色，常在河流、湖泊边活动，以小鱼为食。",
    habitat: "河流、溪流、池塘与湿地",
    tags: ["留鸟", "小型", "水边"],
    color: "#4ba0ff"
  },
  {
    id: 2,
    commonName: "Eurasian Hoopoe",
    chineseName: "戴胜",
    scientificName: "Upupa epops",
    confidenceStatus: "Least Concern",
    bio: "头顶有明显羽冠，鸣声独特，常在草地和农田觅食昆虫。",
    habitat: "农田、果园、开阔林地",
    tags: ["夏候鸟", "地面觅食"],
    color: "#ef8b48"
  },
  {
    id: 3,
    commonName: "Mallard",
    chineseName: "绿头鸭",
    scientificName: "Anas platyrhynchos",
    confidenceStatus: "Least Concern",
    bio: "雁形目常见水禽，雄鸟头部绿色，雌鸟褐色斑驳，适应力强。",
    habitat: "湖泊、河湾、水库",
    tags: ["水鸟", "杂食"],
    color: "#4ca47f"
  },
  {
    id: 4,
    commonName: "European Bee-eater",
    chineseName: "黄喉蜂虎",
    scientificName: "Merops apiaster",
    confidenceStatus: "Least Concern",
    bio: "色彩鲜艳，善于空中捕食昆虫，常集群栖息。",
    habitat: "开阔林地、河岸崖壁",
    tags: ["迁徙", "群居"],
    color: "#66a2ff"
  },
  {
    id: 5,
    commonName: "Long-tailed Tit",
    chineseName: "银喉长尾山雀",
    scientificName: "Aegithalos caudatus",
    confidenceStatus: "Least Concern",
    bio: "圆滚体态，尾羽修长，常成群活动于树冠层。",
    habitat: "灌丛、阔叶林边缘",
    tags: ["群栖", "鸣声活跃"],
    color: "#7a8aa3"
  }
];

function findBirdById(id) {
  return BIRD_KNOWLEDGE.find((item) => item.id === Number(id));
}

function normalizeName(value) {
  return String(value || "")
    .trim()
    .toLowerCase()
    .replace(/\s+/g, " ");
}

function findBirdByName(name) {
  const normalized = normalizeName(name);
  if (!normalized) {
    return null;
  }

  return (
    BIRD_KNOWLEDGE.find((item) => {
      const candidates = [item.commonName, item.chineseName, item.scientificName]
        .map(normalizeName)
        .filter(Boolean);
      return candidates.includes(normalized);
    }) ||
    BIRD_KNOWLEDGE.find((item) => normalizeName(item.commonName).includes(normalized)) ||
    BIRD_KNOWLEDGE.find((item) => normalizeName(item.chineseName).includes(normalized)) ||
    null
  );
}

module.exports = {
  BIRD_KNOWLEDGE,
  findBirdById,
  findBirdByName
};

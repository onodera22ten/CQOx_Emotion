import React from "react";

const Section: React.FC<{ title: string; children: React.ReactNode }> = ({ title, children }) => (
  <section className="space-y-3 bg-white rounded-2xl shadow-sm border border-gray-200 p-5">
    <h2 className="text-lg font-semibold text-gray-900">{title}</h2>
    <div className="text-sm text-gray-700 space-y-2">{children}</div>
  </section>
);

const PrepSection: React.FC<{
  title: string;
  what: React.ReactNode;
  why: React.ReactNode;
  role: React.ReactNode;
  refs?: { label: string; href: string }[];
}> = ({ title, what, why, role, refs }) => (
  <Section title={title}>
    <div className="space-y-3 text-sm text-gray-700">
      <div>
        <p className="font-semibold text-gray-900">何をするか</p>
        <p>{what}</p>
      </div>
      <div>
        <p className="font-semibold text-gray-900">なぜ意味があるのか</p>
        <p>{why}</p>
        {refs && refs.length > 0 && (
          <div className="text-xs text-blue-600 flex flex-wrap gap-2 mt-1">
            {refs.map((ref) => (
              <a key={ref.href} href={ref.href} target="_blank" rel="noopener noreferrer" className="underline">
                {ref.label}
              </a>
            ))}
          </div>
        )}
      </div>
      <div>
        <p className="font-semibold text-gray-900">このツールでの役割</p>
        <p>{role}</p>
      </div>
    </div>
  </Section>
);

export const AboutPage: React.FC = () => {
  return (
    <div className="space-y-8 max-w-3xl">
      <div>
        <h1 className="text-2xl font-semibold text-gray-900">このツールについて</h1>
        <p className="text-sm text-gray-500">
          Emotion CQOx は、人前で話すときのしんどさや涙を自分のデータとして振り返るための「学習ノート」です。診断や治療ではなく、
          「自分にとって何が助けになるか」を丁寧に見つけていくことを目的にしています。
        </p>
      </div>

      <Section title="これは医療ではなく、「学習するノート」です。">
        <ol className="list-decimal list-inside space-y-2">
          <li>
            <strong>医療行為ではありません。</strong> 表示されるグラフや推定効果は、あなたの入力データを元にした統計的な仮説です。診断・治療・予後の保証ではなく、
            次の一歩を考えるための材料です。
          </li>
          <li>
            <strong>強い苦痛には対応できません。</strong> 長期化するつらさや「消えてしまいたい」という気持ちが続く時は、公的窓口や医療機関、信頼できる人に相談してください。
            緊急時は地域の救急・専門機関を優先してください。
          </li>
          <li>
            <strong>5 つの準備は「現時点のベスト仮説」です。</strong> 世界中で使われてきた対処法を参考に選んだもので、万能薬ではありません。根拠の一例:{" "}
            <a
              href="https://sparq.stanford.edu/sites/g/files/sbiybj19021/files/media/file/baikie_wilhelm_2005_-_emotional_and_physical_health_benefits_of_expressive_writing.pdf"
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-600 underline"
            >
              Baikie &amp; Wilhelm (2005)
            </a>
            。
          </li>
          <li>
            <strong>一緒にアップデートしていくツールです。</strong> Episode Draft / Outcome Log / Dashboard のループを回すことで、
            「どの場面で何が助けになるか」という仮説を一緒に育てていきます。
          </li>
        </ol>
      </Section>

      <div>
        <h2 className="text-xl font-semibold text-gray-900 mb-3">なぜこの 5 つの準備なのか</h2>
        <p className="text-sm text-gray-600 mb-4">
          「本当に意味があるのか？」という疑問は重要です。各ステップについて、PDF で提示している根拠と狙いをそのまま掲載します。
        </p>
        <div className="space-y-4">
          <PrepSection
            title="① 10分の書き出し（Expressive Writing）"
            what="今感じているしんどさや怖いイメージ、言いたかったことを 10 分だけ手を止めずに書き続ける練習です。話す予定の内容にこだわらなくても構いません。"
            why={
              <>
                エクスプレッシブ・ライティングとして研究されており、数回に分けて書いた人は心の負担が軽くなり健康指標も改善しやすいと報告されています。
                頭の中でぐるぐるしている内容を文字にすると、「何に一番傷ついているのか」「どこまで話すか」が見える形になり、本番で感情があふれるリスクを下げます。
              </>
            }
            role="Episode Draft で「どれくらい書き出しを行うか」をスライダーで指定し、Outcome Log の結果と合わせて「書き出し量と涙レベル・しんどさの変化」を推定します。"
            refs={[
              {
                label: "PMC: Emotional and Physical Health Benefits of Expressive Writing",
                href: "https://pmc.ncbi.nlm.nih.gov/articles/PMC3830620/",
              },
            ]}
          />
          <PrepSection
            title="② 伝えたい3つのメッセージ（Rule of Three）"
            what="「この面談が終わったとき、最低限これだけは伝わっていてほしい」というポイントを 3 つの短い文にまとめます。"
            why="コミュニケーション研究では、人が覚えやすいメインメッセージは 3 つ前後と繰り返し示されています。伝えたいことを増やしすぎると頭の中がごちゃごちゃになり、あえて 3 つに絞ることで注意の焦点がはっきりし自己批判ではなく「メッセージ」に意識を向けやすくなります。"
            role="Episode Draft で 3 つのメッセージをメモし、Dashboard で「メッセージの明確さ（自己評価）」と伝えられた感のつながりを学習します。"
            refs={[
              {
                label: "Journal Anglo-Saxon: Rule of Three study",
                href: "https://www.journal.unrika.ac.id/index.php/jurnalanglo-saxon/article/download/542/408",
              },
            ]}
          />
          <PrepSection
            title="③ 4-7-8 呼吸法（スローブリージング）"
            what="4 秒吸う → 7 秒息を止める → 8 秒吐くという呼吸サイクルを数分間くり返す練習です。"
            why={
              <>
                ゆっくりした呼吸は自律神経のバランスを整え、一時的な不安やストレスを下げる効果があるとする研究が多数あります。特に「長く吐く／呼吸回数を減らす」タイプは
                交感神経の高ぶりを抑え、体を「休むモード」に切り替える助けになります。
              </>
            }
            role="Episode Draft で練習量や当日のサイクル数を設定し、Outcome ログと組み合わせて「呼吸法が効きやすい条件／効きにくい条件」を個人レベルで学習します。"
            refs={[
              {
                label: "PMC: Slow Breathing and Anxiety",
                href: "https://pmc.ncbi.nlm.nih.gov/articles/PMC10741869/",
              },
              {
                label: "ScienceDirect: Slow Breathing Mechanisms",
                href: "https://www.sciencedirect.com/science/article/pii/S0965229923000249",
              },
            ]}
          />
          <PrepSection
            title="④ 自分で Q&A ロールプレイ（自己ロールプレイ）"
            what="想定される質問や怖い一言を書き出し、自分で質問役と答える側を演じてみる練習です（声に出しても、頭の中でも構いません）。"
            why="不安症や対人恐怖の治療に用いられる CBT の中核は「安全な場でのリハーサルと段階的エクスポージャー」です。想定問答や模擬スピーチを繰り返すことで恐怖が下がり、「話す = 破滅」ではなく「しんどいけれどやり切れる可能性もある」と脳が学習していきます。"
            role="Episode Draft でロールプレイの量を記録し、Dashboard でしんどさ・伝えられた感・関係への影響とのつながりを可視化します。"
            refs={[
              {
                label: "PMC: CBT for Public Speaking Anxiety",
                href: "https://pmc.ncbi.nlm.nih.gov/articles/PMC8475916/",
              },
            ]}
          />
          <PrepSection
            title="⑤ セーフワードを決める（安全ラインの合図）"
            what="「ここまで来たら休憩／話題を変える／次回に回す」という合図の言葉を事前に決めておき、心の安全ラインを明確にします。"
            why="自殺予防の分野では危機が高まったときの行動をまとめたセーフティプランが再発リスクを下げると報告されています。ここでは、それをもっと手前の“心の安全ライン”に縮小し、自分を守るための小さなブレーキとして活用します。"
            role="Episode Draft でセーフワードと使う条件をメモし、Outcome と照合して「事前に決めておくと関係への影響や振り返り時の安心感がどう変わるか」を推定します。"
            refs={[
              {
                label: "CECT Resource Library: Safety Planning",
                href: "https://cectresourcelibrary.info/wp-content/uploads/2021/07/Rogers-et-al_2022_Why-does-safety-planning-prevent-suicidal-behavior.pdf",
              },
            ]}
          />
        </div>
      </div>
    </div>
  );
};

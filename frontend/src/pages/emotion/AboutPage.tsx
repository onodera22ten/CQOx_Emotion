import React from "react";

const Section: React.FC<{ title: string; children: React.ReactNode }> = ({ title, children }) => (
  <section className="space-y-3 bg-white rounded-2xl shadow-sm border border-gray-200 p-5">
    <h2 className="text-lg font-semibold text-gray-900">{title}</h2>
    <div className="text-sm text-gray-700 space-y-2">{children}</div>
  </section>
);

export const AboutPage: React.FC = () => {
  return (
    <div className="space-y-8 max-w-3xl">
      <div>
        <h1 className="text-2xl font-semibold text-gray-900">このツールについて</h1>
        <p className="text-sm text-gray-500">
          Emotion CQOx は、人前で話すときのしんどさや涙を自分の言葉で振り返るための「学習ノート」です。
          医療・診断ではなく「自分にとって何が助けになるか」を一緒に探すことを目的にしています。
        </p>
      </div>

      <Section title="これは医療ではなく、「学習するノート」です。">
        <ol className="list-decimal list-inside space-y-2">
          <li>
            <strong>医療行為ではありません。</strong>
            表示されるグラフや推定効果は、あなたの入力データを元にした統計的な予測です。診断や治療、予後の保証ではなく、
            「仮説」を一緒に考えるための材料です。
          </li>
          <li>
            <strong>強い苦痛には対応できません。</strong>
            つらさが長く続いている・日常生活に支障が出ている・「消えてしまいたい」といった強い気持ちが繰り返し出るときは、
            医療機関や信頼できる人、公的窓口に相談してください。危険を感じたときは地域の救急・専門機関を優先してください。
          </li>
          <li>
            <strong>5 つの準備は「現時点のベスト仮説」です。</strong>
            どの準備も万能薬ではありません。あなたのログをもとに、「どれが助けになりやすいか」を因果推論で少しずつ学習していきます。
          </li>
          <li>
            <strong>一緒にアップデートしていくツールです。</strong>
            準備プランと結果を記録していくことで、「この場面ではこの準備が効きそう」という仮説を一緒に育てていきます。
          </li>
        </ol>
      </Section>

      <div>
        <h2 className="text-xl font-semibold text-gray-900 mb-3">なぜこの5つの準備なのか</h2>
        <p className="text-sm text-gray-600 mb-4">
          「本当に意味があるのか？」という疑問は大切です。Emotion CQOx が採用している 5 つの準備ステップについて、根拠とねらいを簡潔にまとめました。
          どれも万能ではありませんが、「何もしないより少しでも味方になる選択肢」として位置づけています。
        </p>
        <div className="space-y-4">
          <Section title="① 10分の書き出し（Expressive Writing）">
            <p>
              今感じているしんどさや怖いイメージを 10 分間書き続ける練習です。エクスプレッシブ・ライティングの研究では、書くことで心の負担が軽くなると報告されています。
              頭の中でぐるぐるしている内容が言葉になることで、本番の感情爆発を防ぐ助けになります。
            </p>
          </Section>
          <Section title="② 伝えたい3つのメッセージ">
            <p>
              面談後に相手へ最低限伝わっていてほしいポイントを 3 つの短い文にするステップです。コミュニケーション研究の「Rule of Three」にならい、
              伝える核を決めることで焦りを減らします。
            </p>
          </Section>
          <Section title="③ 4-7-8呼吸法">
            <p>
              4 秒吸う→ 7 秒止める→ 8 秒吐く呼吸法。自律神経を整え、緊張を落ち着かせる効果が期待されています。面接前のルーティーンとして組み込むことで心拍の暴走を抑えます。
            </p>
          </Section>
          <Section title="④ 自分でQ&Aロールプレイ">
            <p>
              予想される質問を自分で投げかけ、声に出して答える練習です。恐れている場面を安全にシミュレーションすることで、
              「しんどいけれどやり切れる」感覚を身体で覚えていきます。
            </p>
          </Section>
          <Section title="⑤ セーフワードを決める">
            <p>
              「ここで一度休憩する／話題を変える」という合図の言葉を事前に決めておくステップです。安全ラインを決めることで、自分を追い詰めすぎずに話すバランスを保ちます。
            </p>
          </Section>
        </div>
      </div>
    </div>
  );
};

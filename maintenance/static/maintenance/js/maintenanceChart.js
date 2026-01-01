// DOM이 로드된 후 실행
document.addEventListener('DOMContentLoaded', () => {
  // Recharts 컴포넌트들을 변수에 할당
  const {
      ResponsiveContainer,
      LineChart,
      Line,
      XAxis,
      YAxis,
      CartesianGrid,
      Tooltip,
      Legend
  } = window.Recharts;

  // 데이터 변환 함수
  function transformData(yearlyData, months) {
      return months.map((month, idx) => {
          const monthData = {
              name: `${month}월`
          };
          yearlyData.forEach(room => {
              monthData[`${room.room}호`] = room.monthly_charges[idx];
          });
          return monthData;
      });
  }

  // 색상 배열
  const colors = ['#297777', '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEEAD', '#D4A5A5', '#9B7E7E'];

  // 차트 컴포넌트
  function MaintenanceChart() {
      const chartData = transformData(window._yearlyData || [], window._months || []);
      
      return React.createElement(ResponsiveContainer, { width: '100%', height: '100%' },
          React.createElement(LineChart, { data: chartData },
              React.createElement(CartesianGrid, { strokeDasharray: '3 3' }),
              React.createElement(XAxis, { dataKey: 'name' }),
              React.createElement(YAxis, {
                  tickFormatter: (value) => new Intl.NumberFormat('ko-KR').format(value)
              }),
              React.createElement(Tooltip, {
                  formatter: (value) => new Intl.NumberFormat('ko-KR').format(value)
              }),
              React.createElement(Legend),
              window._yearlyData.map((room, index) => 
                  React.createElement(Line, {
                      key: room.room,
                      type: 'monotone',
                      dataKey: `${room.room}호`,
                      stroke: colors[index % colors.length],
                      strokeWidth: 2
                  })
              )
          )
      );
  }

  // DOM에 렌더링
  const container = document.getElementById('maintenance-chart');
  if (container) {
      const root = ReactDOM.createRoot(container);
      root.render(React.createElement(MaintenanceChart));
  }
});